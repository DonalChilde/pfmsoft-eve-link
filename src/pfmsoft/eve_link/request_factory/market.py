"""Generated request builders for the Market tag."""

from typing import Any
from uuid import UUID, uuid4

from pfmsoft.eve_link import EsiRequest

from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT


def get_characters_character_id_orders(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    character_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """List open market orders placed by a character."""
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
        operation_id="GetCharactersCharacterIdOrders",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_characters_character_id_orders_history(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    character_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """List cancelled and expired market orders placed by a character up to 90 days in the past."""
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
        operation_id="GetCharactersCharacterIdOrdersHistory",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_corporations_corporation_id_orders(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    corporation_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """List open market orders placed on behalf of a corporation."""
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
        operation_id="GetCorporationsCorporationIdOrders",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_corporations_corporation_id_orders_history(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    corporation_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """List cancelled and expired market orders placed on behalf of a corporation up to 90 days in the past."""
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
        operation_id="GetCorporationsCorporationIdOrdersHistory",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request


def get_markets_groups(
    *,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Get a list of item groups This route expires daily at 11:05."""
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
        operation_id="GetMarketsGroups",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_markets_groups_market_group_id(
    *,
    market_group_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Get information on an item group This route expires daily at 11:05."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["market_group_id"] = market_group_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsGroupsMarketGroupId",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_markets_prices(
    *,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of prices."""
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
        operation_id="GetMarketsPrices",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_markets_region_id_history(
    *,
    region_id: int,
    type_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of historical market statistics for the specified type in a region This route expires daily at 11:05."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["region_id"] = region_id
    query_parameters["type_id"] = type_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsRegionIdHistory",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_markets_region_id_orders(
    *,
    region_id: int,
    order_type: str,
    type_id: int | None = None,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of orders in a region."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["region_id"] = region_id
    query_parameters["order_type"] = order_type
    query_parameters["type_id"] = type_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsRegionIdOrders",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_markets_region_id_types(
    *,
    region_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return a list of type IDs that have active orders in the region, for efficient market indexing."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["region_id"] = region_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsRegionIdTypes",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
    )
    return request


def get_markets_structures_structure_id(
    *,
    auth_character_id: int,
    auth_credential_id: UUID,
    structure_id: int,
    accept_language: str | None = ACCEPT_LANGUAGE,
    x_compatibility_date: str | None = X_COMPATIBILITY_DATE,
    x_tenant: str | None = X_TENANT,
) -> EsiRequest:
    """Return all orders in a structure."""
    path_parameters: dict[str, Any] = {}
    query_parameters: dict[str, Any] = {}
    header_parameters: dict[str, Any] = {}

    path_parameters["structure_id"] = structure_id
    header_parameters["Accept-Language"] = accept_language
    header_parameters["X-Compatibility-Date"] = x_compatibility_date
    header_parameters["X-Tenant"] = x_tenant

    # Omit optional parameters that were left as None.
    path_parameters = {k: v for k, v in path_parameters.items() if v is not None}
    query_parameters = {k: v for k, v in query_parameters.items() if v is not None}
    header_parameters = {k: v for k, v in header_parameters.items() if v is not None}

    request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsStructuresStructureId",
        header_parameters=header_parameters,
        path_parameters=path_parameters,
        query_parameters=query_parameters,
        auth_character_id=auth_character_id,
        auth_credential_id=auth_credential_id,
    )
    return request
