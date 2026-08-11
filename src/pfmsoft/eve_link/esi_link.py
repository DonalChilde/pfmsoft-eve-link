"""Library entrypoint for schema-validated ESI request execution.

The EsiLink class is the main API used by library consumers. It coordinates
schema validation, runtime request construction, authorization token lookup,
batch HTTP execution, and response shaping.
"""

import logging
from copy import deepcopy
from pathlib import Path
from types import TracebackType
from typing import Self
from uuid import UUID

import pfmsoft.api_request as api_request
from pfmsoft.api_request.cache import SqliteCacheFactory
from pfmsoft.api_request.rate_limit import AiolimiterRateLimiterFactory
from pfmsoft.api_request.request.models import Responses
from pfmsoft.eve_auth_manager.sqlite.manager import SqliteAuthManager
from pfmsoft.eve_snippets.httpx2.http_session_factory import client_manager

from pfmsoft.eve_link.esi_request.models import (
    EsiRequest,
    EsiRequestGroup,
    EsiResponse,
    EsiResponseGroup,
    FailedEsiResponse,
    RuntimeEsiRequest,
)
from pfmsoft.eve_link.esi_request.runtime_builder import build_runtime_esi_request
from pfmsoft.eve_link.esi_request.validate import (
    EsiRequestValidationErrors,
    validate_esi_request,
)
from pfmsoft.eve_link.schema.cache.schema_cache_disk import SchemaCacheManager
from pfmsoft.eve_link.schema.models import EsiSchema, SchemaOperation
from pfmsoft.eve_link.settings import USER_AGENT, EsiLinkSettings

logger = logging.getLogger(__name__)


class EsiLink:
    """Execute ESI request groups with schema validation and runtime services.

    This class must be used as an async context manager so request and auth
    backends are initialized and cleaned up correctly.
    """

    def __init__(
        self,
        auth_manager_db_path: Path,
        web_cache_path: Path,
        max_rate: float = 20.0,
        time_period: float = 1.0,
    ):
        """Configure an EsiLink instance.

        Args:
            auth_manager_db_path: Path to the SqliteAuthManager database.
            web_cache_path: Path to the HTTP response cache database.
            max_rate: Maximum number of requests per rate-limit window.
            time_period: Window duration in seconds for rate limiting.
        """
        self.api_requester: api_request.ApiRequester | None = None
        self.auth_manager: SqliteAuthManager | None = None
        self.auth_manager_db_path = auth_manager_db_path
        self.web_cache_path = web_cache_path
        self.max_rate = max_rate
        self.time_period = time_period

    async def __aenter__(self) -> Self:
        """Initialize API requester and auth manager resources.

        Returns:
            The initialized EsiLink instance.
        """
        web_cache_factory = SqliteCacheFactory(db_path=self.web_cache_path)
        rate_limiter_factory = AiolimiterRateLimiterFactory(
            max_rate=self.max_rate, time_period=self.time_period
        )
        self.api_requester = api_request.ApiRequester(
            cache_factory=web_cache_factory, rate_limiter_factory=rate_limiter_factory
        )
        self.auth_manager = SqliteAuthManager(db_path=self.auth_manager_db_path)
        await self.api_requester.__aenter__()
        self.auth_manager.__enter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        """Release API requester and auth manager resources."""
        if self.api_requester is not None:
            await self.api_requester.__aexit__(exc_type, exc_value, traceback)
        if self.auth_manager is not None:
            self.auth_manager.__exit__(exc_type, exc_value, traceback)

    def _check_api_requester_initialized(self) -> api_request.ApiRequester:
        """Return initialized ApiRequester instance.

        Returns:
            Initialized ApiRequester.

        Raises:
            RuntimeError: If EsiLink is used outside async context manager scope.
        """
        if self.api_requester is None:
            raise RuntimeError("EsiLink must be used as an async context manager.")
        return self.api_requester

    def _check_auth_manager(self) -> SqliteAuthManager:
        """Return initialized SqliteAuthManager instance.

        Returns:
            Initialized SqliteAuthManager.

        Raises:
            RuntimeError: If EsiLink is used outside async context manager scope.
        """
        if self.auth_manager is None:
            raise RuntimeError("EsiLink must be used as an async context manager.")
        return self.auth_manager

    def _check_operation(
        self, operation_id: str, esi_schema: EsiSchema
    ) -> SchemaOperation:
        """Check if the operation_id exists in the schema.

        Args:
            operation_id (str): The operation ID to check.
            esi_schema (EsiSchema): The schema to check against.

        Returns:
            SchemaOperation: The schema operation corresponding to the operation ID.

        Raises:
            ValueError: If the operation ID is not found in the schema.
        """
        operation = esi_schema.operations.get(operation_id)
        if operation is None:
            raise ValueError(f"Operation ID '{operation_id}' not found in ESI schema.")
        return operation

    async def _attach_access_token_if_required(
        self,
        esi_request: EsiRequest,
        runtime_esi_request: RuntimeEsiRequest,
    ) -> None:
        """Attach access token to runtime request when authorization is required.

        Args:
            esi_request: The ESI request to check.
            runtime_esi_request: Runtime request to mutate with access token.

        Raises:
            ValueError: If authorization tuple is incomplete.
        """
        if not esi_request.has_authorization:
            return
        auth_manager = self._check_auth_manager()
        cred_id = esi_request.auth_credential_id
        character_id = esi_request.auth_character_id
        if cred_id is None or character_id is None:
            raise ValueError(
                "Credential ID and Character ID must be provided for authorized requests."
            )
        access_token = auth_manager.get_character(cred_id, character_id).access_token
        runtime_esi_request.access_token = access_token

    async def make_request(
        self, esi_request: EsiRequest, schema: EsiSchema
    ) -> EsiResponse | FailedEsiResponse:
        """Validate, execute, and return a single ESI request response.

        Args:
            esi_request: The ESI request to execute.
            schema: Schema used for operation lookup and validation.

        Returns:
            EsiResponse | FailedEsiResponse: The response for the ESI request.

        Raises:
            RuntimeError: If EsiLink is used outside async context manager scope.
            EsiRequestValidationErrors: If the request fails schema validation.
            Exception: Any backend execution exception from request or auth layers.
        """
        request_group = EsiRequestGroup(
            name="single_request_group",
            description="A group containing a single ESI request.",
            requests={esi_request.request_id: esi_request},
        )
        response_group = await self.make_requests(request_group, schema)
        if esi_request.request_id in response_group.failed_responses:
            return response_group.failed_responses[esi_request.request_id]
        elif esi_request.request_id in response_group.successful_responses:
            return response_group.successful_responses[esi_request.request_id]
        else:
            raise RuntimeError(
                f"Response for request ID {esi_request.request_id} not found in response group."
            )

    async def make_requests(
        self,
        esi_requests: EsiRequestGroup,
        schema: EsiSchema,
    ) -> EsiResponseGroup:
        """Validate, execute, and group responses for an ESI request batch.

        Args:
            esi_requests: ESI requests to execute.
            schema: Schema used for operation lookup and validation.

        Returns:
            Grouped successful and failed responses keyed by runtime request key.

        Raises:
            RuntimeError: If EsiLink is used outside async context manager scope.
            EsiRequestValidationErrors: If any request fails schema validation.
            Exception: Any backend execution exception from request or auth layers.
        """
        requester = self._check_api_requester_initialized()

        runtime_requests: dict[UUID, RuntimeEsiRequest] = {}
        for _, request in esi_requests.requests.items():
            self.validate_request(request, schema)
            runtime_request = build_runtime_esi_request(request, schema)
            await self._attach_access_token_if_required(request, runtime_request)
            runtime_requests[runtime_request.request_key] = runtime_request

        request_objects = {
            key: _make_request_from_runtime_request(request)
            for key, request in runtime_requests.items()
        }
        responses: Responses = await requester.process_requests(request_objects)
        esi_responses = _make_esi_response_group(
            responses, esi_requests, runtime_requests
        )
        return esi_responses

    @staticmethod
    def validate_request(
        esi_request: EsiRequest,
        schema: EsiSchema,
    ) -> None:
        """Validate one ESI request against the provided schema.

        Args:
            esi_request: The ESI request to validate.
            schema: Schema used for validation rules.

        Raises:
            EsiRequestValidationErrors: If request data violates schema-derived rules.
        """
        try:
            validate_esi_request(esi_request, schema)
        except EsiRequestValidationErrors as e:
            logger.error("Validation failed for request %s: %s", esi_request, e)
            raise


def _make_esi_response_group(
    responses: Responses,
    requests: EsiRequestGroup,
    runtime_requests: dict[UUID, RuntimeEsiRequest],
) -> EsiResponseGroup:
    """Convert api_request response groups into EsiResponseGroup containers.

    Collects successful and failed responses, purges access tokens from runtime requests,
    and constructs EsiResponse and FailedEsiResponse objects.
    """
    successful_responses: dict[UUID, EsiResponse] = {}
    failed_responses: dict[UUID, FailedEsiResponse] = {}
    for request_id, response in responses.successful.items():
        runtime_request = runtime_requests[request_id]
        runtime_request.purge_access_token()
        successful_responses[request_id] = EsiResponse(
            esi_request=requests.requests[request_id],
            esi_runtime_request=runtime_request,
            response=response,
        )
    for request_id, response in responses.failed.items():
        runtime_request = runtime_requests[request_id]
        runtime_request.purge_access_token()
        failed_responses[request_id] = FailedEsiResponse(
            esi_request=deepcopy(requests.requests[request_id]),
            esi_runtime_request=runtime_request,
            failed_response=response,
        )
    return EsiResponseGroup(
        name=requests.name,
        description=requests.description,
        successful_responses=successful_responses,
        failed_responses=failed_responses,
    )


def _make_request_from_runtime_request(
    runtime_request: RuntimeEsiRequest,
) -> api_request.Request:
    """Convert RuntimeEsiRequest to api_request.Request.

    Args:
        runtime_request: Runtime ESI request to convert.

    Returns:
        Converted api_request.Request object.
    """
    return api_request.Request(
        request_key=runtime_request.request_key,
        method=runtime_request.method,
        url=runtime_request.url,
        headers=runtime_request.headers_with_authorization,
        body=runtime_request.json_payload,
        parameters=runtime_request.query_parameters,
        cache_key=runtime_request.cache_key,
        rate_key=runtime_request.rate_limit_key,
    )


class SimpleRequests:
    def __init__(self, settings: EsiLinkSettings) -> None:
        """A simple wrapper for executing ESI requests with schema validation.

        The only state saved by this class is the EsiLinkSettings object, which is used
        to configure the EsiLink instance and schema cache manager. While the factory
        functions for creating EsiLink and SchemaCacheManager instances are useful for
        all situations, the other functions are intended for one-off scripts or commands
        that need to execute a single request or a small batch of requests without
        managing the EsiLink context directly.

        Longer lived applications that execute multiple requests should use the
        SchemaCacheManager and EsiLink class directly, as it is more efficient to keep
        the EsiLink instance open and reuse it for multiple requests.
        """
        self.settings = settings

    def get_schema(self, compatibility_date: str | None = None) -> EsiSchema:
        """Fetches an ESI schema from the EsiLink schema cache.

        This function retrieves the ESI schema from the local cache managed by the
        SchemaCacheManager. If a compatibility date is provided, it fetches the schema
        corresponding to that date; otherwise, it retrieves the latest available schema.

        This function will check for new schema updates from the ESI schema repository
        once per downtime before returning the schema.

        It is suitable for one-off scripts or commands. When executing multiple requests,
        consider using SchemaCacheManager directly to avoid repeated cache lookups.

        Args:
            compatibility_date: Optional compatibility date in YYYY-MM-DD format.
                If not provided, the latest schema is fetched.

        Returns:
            The EsiSchema object for the specified compatibility date or the latest
                schema if no date is provided.

        Raises:
            ValueError: If no cached schema entries exist.
        """
        schema_manager = self.schema_cache_manager_factory()
        with client_manager(USER_AGENT) as session:
            schema_manager.fetch_updates(session=session)
        if compatibility_date is not None:
            esi_schema = schema_manager.load(compatibility_date=compatibility_date)
        else:
            esi_schema = schema_manager.latest_schema()
        return esi_schema

    def schema_cache_manager_factory(self) -> SchemaCacheManager:
        """Factory function to create an instance of SchemaCacheManager from settings.

        Returns:
            SchemaCacheManager: An instance of the SchemaCacheManager class.
        """
        return SchemaCacheManager(cache_directory=self.settings.schema_cache_directory)

    def esi_link_factory(self) -> EsiLink:
        """Factory function to create an instance of EsiLink from settings.

        Returns:
            EsiLink: An instance of the EsiLink class.
        """
        return EsiLink(
            auth_manager_db_path=self.settings.eve_auth_manager_settings.authorization_database_path,
            web_cache_path=self.settings.api_request_settings.web_cache_path,
            max_rate=self.settings.max_rate,
            time_period=self.settings.time_period,
        )

    async def make_request(
        self, esi_request: EsiRequest, schema: EsiSchema
    ) -> EsiResponse | FailedEsiResponse:
        """Validate, execute, and return a single ESI request response.

        This function wraps the EsiLink class to provide a simple interface for executing
        a single ESI request. It creates a temporary EsiLink instance, validates the request
        against the provided schema, and executes it. The response is returned as either
        an EsiResponse or a FailedEsiResponse, depending on the outcome of the request.

        When used in situations where multiple requests need to be executed, consider using
        the EsiLink class directly to avoid the overhead of creating and closing multiple
        instances with their associated resources.

        Args:
            esi_request: The ESI request to execute.
            schema: The ESI schema for validation.

        Returns:
            EsiResponse if the request is successful, otherwise FailedEsiResponse.
        """
        async with self.esi_link_factory() as esi_link:
            response = await esi_link.make_request(
                esi_request=esi_request, schema=schema
            )
            return response

    async def make_requests(
        self, esi_requests: EsiRequestGroup, schema: EsiSchema
    ) -> EsiResponseGroup:
        """Validate, execute, and return a group of ESI request responses.

        This function wraps the EsiLink class to provide a simple interface for executing
        a group of ESI requests. It creates a temporary EsiLink instance, validates the
        requests against the provided schema, and executes them. The responses are returned
        as an EsiResponseGroup, containing both successful and failed responses.

        When used in situations where multiple requests need to be executed, consider using
        the EsiLink class directly to avoid the overhead of creating and closing multiple
        instances.

        Args:
            esi_requests: The group of ESI requests to execute.
            schema: The ESI schema for validation.

        Returns:
            EsiResponseGroup: The group of ESI request responses.
        """
        async with self.esi_link_factory() as esi_link:
            response_group = await esi_link.make_requests(esi_requests, schema)
            return response_group
