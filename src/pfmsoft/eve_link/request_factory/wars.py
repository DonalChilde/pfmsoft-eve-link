"""Generated request builders for the Wars tag."""

from typing import Any
from uuid import uuid4

from pfmsoft.eve_link import EsiRequest

from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT


def get_wars(
    *,
    max_war_id: int | None = None,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of wars."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    query_parameters["max_war_id"] = max_war_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetWars",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_wars_war_id(
    *,
    war_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return details about a war."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["war_id"] = war_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetWarsWarId",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_wars_war_id_killmails(
    *,
    war_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of kills related to a war."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["war_id"] = war_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetWarsWarIdKillmails",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request
