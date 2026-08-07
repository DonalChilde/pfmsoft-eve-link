"""Generated request builders for the Status tag."""

from typing import Any
from uuid import uuid4

from pfmsoft.eve_link.esi_request.models import EsiRequest

from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT


def get_status(
    *,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """EVE Server status."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetStatus",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request
