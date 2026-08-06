"""Generated request builders for the Routes tag."""

from typing import Any
from uuid import uuid4

from pfmsoft.eve_link.esi_request.models import EsiRequest

from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT


def post_route(
    *,
    request_body: Any,
    origin_system_id: int,
    destination_system_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Calculate the systems between the given origin and destination."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["origin_system_id"] = origin_system_id
    path_parameters["destination_system_id"] = destination_system_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="PostRoute",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        request_body=request_body,
    )
    return request
