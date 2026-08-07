"""Generated request builders for the Assets tag."""

from typing import Any
from uuid import UUID, uuid4

from pfmsoft.eve_link.esi_request.models import EsiRequest

from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT


def get_characters_character_id_assets(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    character_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of the characters assets."""
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
        operation_id="GetCharactersCharacterIdAssets",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_corporations_corporation_id_assets(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    corporation_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of the corporation assets."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["corporation_id"] = corporation_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetCorporationsCorporationIdAssets",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def post_characters_character_id_assets_locations(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    request_body: Any,
    character_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return locations for a set of item ids, which you can get from character assets endpoint. Coordinates for items in hangars or stations are set to (0,0,0)."""
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
        operation_id="PostCharactersCharacterIdAssetsLocations",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
        request_body=request_body,
    )
    return request


def post_characters_character_id_assets_names(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    request_body: Any,
    character_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return names for a set of item ids, which you can get from character assets endpoint. Typically used for items that can customize names, like containers or ships."""
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
        operation_id="PostCharactersCharacterIdAssetsNames",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
        request_body=request_body,
    )
    return request


def post_corporations_corporation_id_assets_locations(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    request_body: Any,
    corporation_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return locations for a set of item ids, which you can get from corporation assets endpoint. Coordinates for items in hangars or stations are set to (0,0,0)."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["corporation_id"] = corporation_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="PostCorporationsCorporationIdAssetsLocations",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
        request_body=request_body,
    )
    return request


def post_corporations_corporation_id_assets_names(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    request_body: Any,
    corporation_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return names for a set of item ids, which you can get from corporation assets endpoint. Only valid for items that can customize names, like containers or ships."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["corporation_id"] = corporation_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="PostCorporationsCorporationIdAssetsNames",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
        request_body=request_body,
    )
    return request
