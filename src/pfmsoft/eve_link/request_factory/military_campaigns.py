"""Generated request builders for the Military Campaigns tag."""

from typing import Any
from uuid import UUID, uuid4

from pfmsoft.eve_link import EsiRequest

from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT


def get_characters_military_campaigns_objectives_listing(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    character_id: int,
    after: str | None = None,
    before: str | None = None,
    limit: int | None = None,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Listing of the military campaign objectives the character has participated in."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["character_id"] = character_id
    query_parameters["after"] = after
    query_parameters["before"] = before
    query_parameters["limit"] = limit
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetCharactersMilitaryCampaignsObjectivesListing",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_characters_military_campaigns_objectives_participation(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    character_id: int,
    objective_id: str,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Show your participation in a military campaign objective."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["character_id"] = character_id
    path_parameters["objective_id"] = objective_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetCharactersMilitaryCampaignsObjectivesParticipation",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_military_campaigns_detail(
    *,
    campaign_id: str,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Get the details of a military campaign."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["campaign_id"] = campaign_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMilitaryCampaignsDetail",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_military_campaigns_listing(
    *,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Listing of all active military campaigns."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMilitaryCampaignsListing",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_military_campaigns_objectives_detail(
    *,
    campaign_id: str,
    objective_id: str,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Get the details of an objective of a military campaign."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["campaign_id"] = campaign_id
    path_parameters["objective_id"] = objective_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMilitaryCampaignsObjectivesDetail",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_military_campaigns_objectives_listing(
    *,
    campaign_id: str,
    after: str | None = None,
    before: str | None = None,
    limit: int | None = None,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Listing of all active, completed or expired objectives of a military campaign."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["campaign_id"] = campaign_id
    query_parameters["after"] = after
    query_parameters["before"] = before
    query_parameters["limit"] = limit
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMilitaryCampaignsObjectivesListing",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request
