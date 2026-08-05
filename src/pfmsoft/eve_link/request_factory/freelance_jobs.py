"""Generated request builders for the Freelance Jobs tag."""

from typing import Any
from uuid import UUID, uuid4

from pfmsoft.eve_link import EsiRequest

from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT


def get_characters_freelance_jobs_listing(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    character_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Listing of all freelance jobs you are actively participating in."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["character_id"] = character_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetCharactersFreelanceJobsListing",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_characters_freelance_jobs_participation(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    character_id: int,
    job_id: str,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Show your participation in a freelance job."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["character_id"] = character_id
    path_parameters["job_id"] = job_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetCharactersFreelanceJobsParticipation",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_corporations_freelance_jobs_listing(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    corporation_id: int,
    after: str | None = None,
    before: str | None = None,
    limit: int | None = None,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Listing of all freelance jobs for your corporation."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["corporation_id"] = corporation_id
    query_parameters["after"] = after
    query_parameters["before"] = before
    query_parameters["limit"] = limit
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetCorporationsFreelanceJobsListing",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_corporations_freelance_jobs_participants(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    corporation_id: int,
    job_id: str,
    after: str | None = None,
    before: str | None = None,
    limit: int | None = None,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Listing of all participants of a freelance job."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["corporation_id"] = corporation_id
    path_parameters["job_id"] = job_id
    query_parameters["after"] = after
    query_parameters["before"] = before
    query_parameters["limit"] = limit
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetCorporationsFreelanceJobsParticipants",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_freelance_jobs_detail(
    *,
    job_id: str,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Get the details of a freelance job. Jobs without an ACL (public jobs) does not require authentication. Jobs with an ACL requires authentication, and requires that the character is: - An active participant of the job, or - A freelance job manager for the corporation that owns the job."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["job_id"] = job_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetFreelanceJobsDetail",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_freelance_jobs_listing(
    *,
    after: str | None = None,
    before: str | None = None,
    limit: int | None = None,
    corporation_id: int | None = None,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Listing of all public freelance jobs."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    query_parameters["after"] = after
    query_parameters["before"] = before
    query_parameters["limit"] = limit
    query_parameters["corporation_id"] = corporation_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetFreelanceJobsListing",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request
