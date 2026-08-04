"""Data models for ESI request input, runtime request state, and responses.

These models define serialization and token-redaction boundaries for request and
response payloads used by both CLI and library code.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4, uuid5

from pfmsoft.api_request import Response
from pfmsoft.api_request.request.models import FailedResponse
from pydantic import RootModel
from whenever import Instant


class UserSettableHeaders(StrEnum):
    ACCEPT_LANGUAGE = "Accept-Language"
    X_TENANT = "X-Tenant"
    X_COMPATIBILITY_DATE = "X-Compatibility-Date"


@dataclass(slots=True, kw_only=True)
class EsiRequest:
    """Represents a single ESI request to be executed.

    Can be loaded from a file or created programmatically. The request_id is used to
    identify the request.

    Requests can be be contained in a RequestGroup, and the request_id is used
    to link the Request to its RuntimeRequest, and to the final EsiResponse.
    """

    request_id: UUID = field(default_factory=uuid4)
    """The unique identifier for the request. This is used to link the request to various 
        objects during the request lifecycle."""
    name: str | None = None
    """An optional name for the request. This is used for documentation purposes, 
        and can be used to provide context for the request when viewing it in a UI or in 
        logs."""
    description: str | None = None
    """An optional description of the request. This is used for documentation purposes, 
        and can be used to provide context for the request when viewing it in a UI or in 
        logs."""
    operation_id: str
    """The operation ID of the request, corresponding to the operationId in the ESI 
        OpenAPI schema."""
    path_parameters: dict[str, str | int | float] = field(
        default_factory=dict[str, str | int | float]
    )
    """The path parameters for the request, if applicable. This is used to fill in the 
        path parameters in the URL template."""
    query_parameters: dict[str, str | int | float] = field(
        default_factory=dict[str, str | int | float]
    )
    """The query parameters for the request, if applicable.
    
    This is used to fill in the query parameters in the URL template.
    
    NOTE: The page parameter is handled automatically by eve-link, and should not 
        be set manually. If it is set, it will raise a validation error. This is to help 
        normalize cache keys, which rely on predictable parameters.
    """
    header_parameters: dict[str, str] = field(default_factory=dict[str, str])
    """The header parameters for the request, if applicable. 
    
        Acceptable headers are:
        - Accept-Language
        - X-Tenant
        - X-Compatibility-Date
        
        Do not use this to set:
        
        - If-None-Match
        - If-Modified-Since headers. 

        Those are set at runtime during HTTP execution."""
    json_payload: Any | None = None
    """The JSON payload of the request, if applicable. This is used for POST, PUT, and PATCH 
        requests."""
    character_id: int | None = None
    """The character ID used for authorization."""
    credential_id: UUID | None = None
    """The credential ID for authorization. This is used to link the authorization
        to the credential that was used to obtain it. This UUID is obtained from the 
        credential manager that provides the access token."""

    @property
    def has_authorization(self) -> bool:
        """Check if the request has an authorization."""
        return self.character_id is not None and self.credential_id is not None

    @property
    def authorization_slug(self) -> UUID:
        """Get the authorization slug for the authorization.

        This is a UUID that is generated from the character ID and credential ID, and is
        used as part of the cache key to differentiate between different cached
        authorized requests.

        Returns:
            The authorization slug for the authorization.
        """
        if not self.has_authorization:
            raise ValueError(
                "Cannot generate authorization key without both character_id and credential_id."
            )
        return uuid5(self.credential_id, str(self.character_id))  # type: ignore


EsiRequestRoot = RootModel[EsiRequest]


@dataclass(slots=True, kw_only=True)
class RuntimeEsiRequest:
    request_key: UUID
    """The unique key for this runtime request."""
    url: str
    """The URL for this runtime request."""

    method: str
    """The HTTP method for this runtime request."""
    cache_key: UUID | None
    """The cache key for this runtime request, if any."""

    rate_limit_key: str
    """The rate limit key for this runtime request, if any."""

    headers: dict[str, str] = field(default_factory=dict[str, str])
    """The headers for this runtime request."""

    query_parameters: dict[str, str | int | float] = field(
        default_factory=dict[str, str | int | float]
    )
    """The query parameters for this runtime request."""
    json_payload: dict[str, Any] | None = None
    """The JSON payload for this runtime request, if any."""
    access_token: str | None = None
    """The access token for this runtime request, if any."""

    def purge_access_token(self) -> None:
        """Purge the access token for this runtime request.

        THIS SHOULD BE CALLED BEFORE SERIALIZATION TO UNTRUSTED DESTINATIONS.

        If the access token is already `None`, this method does nothing.
        Otherwise, it sets the access token to `"REDACTED"`.
        """
        if self.access_token is None:
            return
        self.access_token = "REDACTED"

    @property
    def headers_with_authorization(self) -> dict[str, str]:
        """Return the combined headers for this runtime request.

        This includes the runtime headers, and the Authorization header if an access
        token is present.

        """
        combined = dict(self.headers)
        if self.access_token is not None:
            combined["Authorization"] = f"Bearer {self.access_token}"
        return combined


@dataclass(slots=True, kw_only=True, frozen=True)
class EsiResponse:
    esi_request: EsiRequest
    """The request that generated this response."""
    esi_runtime_request: RuntimeEsiRequest
    """The request that generated this response."""
    response: Response
    """The response associated with this EsiResponse."""

    def serialize(self, indent: int | None = None) -> str:
        """Serialize the EsiResponse."""
        return EsiResponseRoot(root=self).model_dump_json(indent=indent)

    @property
    def response_data(self) -> Any:
        """Return the JSON response data associated with this EsiResponse."""
        return self.response.json

    @property
    def received_at_instant(self) -> Instant:
        """Return the instant at which the response was received."""
        return self.response.metadata.received_at

    @property
    def expires_at_instant(self) -> Instant | None:
        """Return the instant at which the response expires, if any."""
        return (
            Instant.from_timestamp(self.response.metadata.expires_at)
            if self.response.metadata.expires_at
            else None
        )

    def simple_response(self) -> SimplifiedEsiResponse:
        """Return a simplified version of this EsiResponse.

        This is useful for serialization and deserialization, as it removes the
        response metadata and other details that are not needed for most use cases.
        """
        return SimplifiedEsiResponse(
            esi_request=self.esi_request,
            response_data=self.response_data,
            received_at_instant=self.received_at_instant,
            expires_at_instant=self.expires_at_instant,
        )


EsiResponseRoot = RootModel[EsiResponse]


@dataclass(slots=True, kw_only=True)
class SimplifiedEsiResponse:
    esi_request: EsiRequest
    """The request that generated this response."""
    response_data: Any
    """The JSON response data associated with this SimplifiedEsiResponse."""
    received_at_instant: Instant
    """The instant at which the response was received."""
    expires_at_instant: Instant | None
    """The instant at which the response expires, if any."""

    def serialize(self, indent: int | None = None) -> str:
        """Serialize the SimplifiedEsiResponse."""
        return SimplifiedEsiResponseRoot(root=self).model_dump_json(indent=indent)


SimplifiedEsiResponseRoot = RootModel[SimplifiedEsiResponse]


@dataclass(slots=True, kw_only=True, frozen=True)
class FailedEsiResponse:
    esi_request: EsiRequest
    """The request that generated this failed response."""
    esi_runtime_request: RuntimeEsiRequest
    """The request that generated this failed response."""
    failed_response: FailedResponse
    """The failed response associated with this FailedEsiResponse."""

    def serialize(self, indent: int | None = None) -> str:
        """Serialize the FailedEsiResponse."""
        return FailedEsiResponseRoot(root=self).model_dump_json(indent=indent)


FailedEsiResponseRoot = RootModel[FailedEsiResponse]


# NOTE: This is for a future possible feature to make it easier to hand code requests,
# as the UUID could be generated on deserialization. These would be converted to
# EsiRequestGroup objects for runtime execution. This is not currently used, but is
# left here for future consideration.
# @dataclass(slots=True, kw_only=True)
# class EsiRequestList:
#     name: str | None = None
#     """The name of this list of runtime ESI requests."""
#     description: str | None = None
#     """An optional description of this list of runtime ESI requests."""
#     requests: list[EsiRequest] = field(default_factory=list[EsiRequest])
#     """The list of ESI requests."""


# EsiRequestListRoot = RootModel[EsiRequestList]


@dataclass(slots=True, kw_only=True)
class EsiRequestGroup:
    name: str | None = None
    """The name of this group of runtime ESI requests."""
    description: str | None = None
    """An optional description of this group of runtime ESI requests."""
    requests: dict[UUID, EsiRequest] = field(default_factory=dict[UUID, EsiRequest])
    """The dict of  ESI requests in this group."""


EsiRequestGroupRoot = RootModel[EsiRequestGroup]


# @dataclass(slots=True, kw_only=True)
# class EsiResponseList(EsiRequestList):
#     successful_responses: dict[UUID, EsiResponse] = field(
#         default_factory=dict[UUID, EsiResponse]
#     )
#     """The dict of successful ESI responses."""
#     failed_responses: dict[UUID, FailedEsiResponse] = field(
#         default_factory=dict[UUID, FailedEsiResponse]
#     )
#     """The dict of failed ESI responses."""

#     def purge_tokens(self) -> None:
#         """Purge the access tokens from all successful and failed ESI responses."""
#         for response in self.successful_responses.values():
#             response.esi_runtime_request.purge_access_token()
#         for failed_response in self.failed_responses.values():
#             failed_response.esi_runtime_request.purge_access_token()


# EsiResponseListRoot = RootModel[EsiResponseList]


# FIXME rethink the response models, and whether to include the request. and if so, how to.
# FIXME make the way this is handled the same with single responses and response groups. The request is not needed for the response, but it is useful for debugging and logging. It is also useful for serialization and deserialization, as it allows the request to be reconstructed from the response. However, it is not needed for the response itself, and it may be better to separate the request from the response in the future.
# Maybe make a separate model? EsiResponseSingle?
# @dataclass(slots=True, kw_only=True)
# class ResolvedRequest:
#     request: EsiRequest
#     """The request that generated this response."""
#     response: EsiResponse | FailedEsiResponse
#     """The response associated with this EsiResponseSingle."""


# @dataclass(slots=True, kw_only=True)
# class ResolvedRequestGroup:
#     successful_requests: dict[UUID, EsiResponse] = field(
#         default_factory=dict[UUID, EsiResponse]
#     )
#     """The dict of successful ESI requests and responses in this group."""
#     failed_requests: dict[UUID, FailedEsiResponse] = field(
#         default_factory=dict[UUID, FailedEsiResponse]
#     )
#     """The dict of failed ESI requests and responses in this group."""


@dataclass(slots=True, kw_only=True)
class EsiResponseGroup:
    name: str | None = None
    """The name of this group of runtime ESI responses."""
    description: str | None = None
    """An optional description of this group of runtime ESI responses."""
    successful_responses: dict[UUID, EsiResponse] = field(
        default_factory=dict[UUID, EsiResponse]
    )
    """The dict of successful ESI responses in this group."""
    failed_responses: dict[UUID, FailedEsiResponse] = field(
        default_factory=dict[UUID, FailedEsiResponse]
    )
    """The dict of failed ESI responses in this group."""

    # def _purge_secrets(self) -> None:
    #     """Purge the access tokens from all successful and failed ESI responses in this group."""
    #     for response in self.successful_responses.values():
    #         response._purge_secrets()  # type: ignore
    #     for failed_response in self.failed_responses.values():
    #         failed_response._purge_secrets()  # type: ignore

    def serialize(self, indent: int | None = None) -> str:
        """Purge secrets and serialize the EsiResponseGroup to a JSON string."""
        return EsiResponseGroupRoot(root=self).model_dump_json(indent=indent)


EsiResponseGroupRoot = RootModel[EsiResponseGroup]
