"""Tests for schema-driven request builder generation."""

from pfmsoft.eve_link.request_builder import generate_request_builders
from pfmsoft.eve_link.schema.models import EsiSchema


def test_generate_request_builders_renders_grouped_functions() -> None:
    """Generate a module containing grouped request builder functions."""
    schema = EsiSchema(
        dereferenced_schema={
            "openapi": "3.0.0",
            "info": {"version": "2026-06-09"},
            "servers": [{"url": "https://esi.evetech.net/latest"}],
            "paths": {
                "/markets/groups/": {
                    "get": {
                        "operationId": "GetMarketsGroups",
                        "tags": ["Market"],
                        "description": "Get a list of market groups.\nThis route expires daily.",
                        "parameters": [
                            {
                                "name": "name",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "page",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "integer"},
                            },
                            {
                                "name": "market_group_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            },
                            {
                                "name": "Accept-Language",
                                "in": "header",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {"200": {"description": "OK"}},
                        "x-compatibility-date": "2026-06-09",
                    }
                }
            },
        }
    )

    generated = generate_request_builders(
        schema=schema,
        package_name="generated_requests",
    )
    init_source = generated.files["__init__.py"]
    market_source = generated.files["market.py"]

    assert 'X_COMPATIBILITY_DATE: str = "2026-06-09"' in init_source
    assert 'ACCEPT_LANGUAGE: LangType = "en"' in init_source
    assert 'X_TENANT: str = "tranquility"' in init_source
    assert "from . import market" in init_source
    assert "__all__ = [" in init_source
    assert '"market",' in init_source
    assert "get_markets_groups" not in init_source
    assert (
        "from . import ACCEPT_LANGUAGE, X_COMPATIBILITY_DATE, X_TENANT" in market_source
    )
    assert "def get_markets_groups(" in market_source
    assert '"""Get a list of market groups.' in market_source
    assert "name: str | None = None" in market_source
    assert "accept_language: str | None = ACCEPT_LANGUAGE" in market_source
    assert "market_group_id: int" in market_source
    assert "page" not in market_source


def test_generate_request_builders_uses_constant_defaults_for_known_headers() -> None:
    """Render known header defaults even when the schema marks them as required."""
    schema = EsiSchema(
        dereferenced_schema={
            "openapi": "3.0.0",
            "info": {"version": "2026-06-09"},
            "servers": [{"url": "https://esi.evetech.net/latest"}],
            "paths": {
                "/markets/groups/": {
                    "get": {
                        "operationId": "GetMarketsGroups",
                        "tags": ["Market"],
                        "description": "Get a list of market groups.",
                        "parameters": [
                            {
                                "name": "X-Compatibility-Date",
                                "in": "header",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": "OK"}},
                        "x-compatibility-date": "2026-06-09",
                    }
                }
            },
        }
    )

    generated = generate_request_builders(
        schema=schema,
        package_name="generated_requests",
    )
    market_source = generated.files["market.py"]

    assert "x_compatibility_date: str | None = X_COMPATIBILITY_DATE" in market_source


def test_generate_request_builders_builds_parameter_dicts_for_request() -> None:
    """Generate request bodies that populate headers, path, and query parameter dicts."""
    schema = EsiSchema(
        dereferenced_schema={
            "openapi": "3.0.0",
            "info": {"version": "2026-06-09"},
            "servers": [{"url": "https://esi.evetech.net/latest"}],
            "paths": {
                "/markets/groups/{market_group_id}/": {
                    "get": {
                        "operationId": "GetMarketsGroups",
                        "tags": ["Market"],
                        "description": "Get a list of market groups.",
                        "parameters": [
                            {
                                "name": "market_group_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            },
                            {
                                "name": "name",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "Accept-Language",
                                "in": "header",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {"200": {"description": "OK"}},
                        "x-compatibility-date": "2026-06-09",
                    }
                }
            },
        }
    )

    generated = generate_request_builders(
        schema=schema,
        package_name="generated_requests",
    )
    market_source = generated.files["market.py"]

    assert 'header_parameters["Accept-Language"] = accept_language' in market_source
    assert 'path_parameters["market_group_id"] = market_group_id' in market_source
    assert 'query_parameters["name"] = name' in market_source
    assert "header_parameters=header_parameters" in market_source
    assert "path_parameters=path_parameters" in market_source
    assert "query_parameters=query_parameters" in market_source


def test_generate_request_builders_respects_excluded_parameter_names() -> None:
    """Allow callers to exclude parameters by name."""
    schema = EsiSchema(
        dereferenced_schema={
            "openapi": "3.0.0",
            "info": {"version": "2026-06-09"},
            "servers": [{"url": "https://esi.evetech.net/latest"}],
            "paths": {
                "/markets/groups/": {
                    "get": {
                        "operationId": "GetMarketsGroups",
                        "tags": ["Market"],
                        "description": "Get a list of market groups.",
                        "parameters": [
                            {
                                "name": "name",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                            {
                                "name": "market_group_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "integer"},
                            },
                            {
                                "name": "Accept-Language",
                                "in": "header",
                                "required": False,
                                "schema": {"type": "string"},
                            },
                        ],
                        "responses": {"200": {"description": "OK"}},
                        "x-compatibility-date": "2026-06-09",
                    }
                }
            },
        }
    )

    generated = generate_request_builders(
        schema=schema,
        package_name="generated_requests",
        exclude=frozenset({"name", "Accept-Language"}),
    )
    market_source = generated.files["market.py"]

    assert "name: str | None = None" not in market_source
    assert "accept_language" not in market_source
    assert "market_group_id: int" in market_source


def test_generate_request_builders_only_passes_request_body_when_needed() -> None:
    """Require request_body for body-capable operations without adding it otherwise."""
    schema = EsiSchema(
        dereferenced_schema={
            "openapi": "3.0.0",
            "info": {"version": "2026-06-09"},
            "servers": [{"url": "https://esi.evetech.net/latest"}],
            "paths": {
                "/markets/groups/": {
                    "get": {
                        "operationId": "GetMarketsGroups",
                        "tags": ["Market"],
                        "description": "Get a list of market groups.",
                        "parameters": [],
                        "responses": {"200": {"description": "OK"}},
                        "x-compatibility-date": "2026-06-09",
                    },
                    "post": {
                        "operationId": "PostMarketsGroups",
                        "tags": ["Market"],
                        "description": "Create a market group.",
                        "parameters": [],
                        "requestBody": {
                            "content": {"application/json": {"schema": {}}}
                        },
                        "responses": {"200": {"description": "OK"}},
                        "x-compatibility-date": "2026-06-09",
                    },
                }
            },
        }
    )

    generated = generate_request_builders(
        schema=schema,
        package_name="generated_requests",
    )
    market_source = generated.files["market.py"]

    assert "def get_markets_groups(" in market_source
    assert (
        "request_body"
        not in market_source.split("def get_markets_groups(", 1)[1].split(
            "def post_markets_groups(", 1
        )[0]
    )
    assert "request_body: Any" in market_source
    assert "request_body: Any | None = None" not in market_source
    assert "request_body=request_body" in market_source


def test_generate_request_builders_requires_auth_arguments_for_authenticated_ops() -> (
    None
):
    """Authenticated operations should expose auth arguments and populate them."""
    schema = EsiSchema(
        dereferenced_schema={
            "openapi": "3.0.0",
            "info": {"version": "2026-06-09"},
            "servers": [{"url": "https://esi.evetech.net/latest"}],
            "paths": {
                "/markets/groups/": {
                    "get": {
                        "operationId": "GetMarketsGroups",
                        "tags": ["Market"],
                        "description": "Get a list of market groups.",
                        "parameters": [],
                        "security": [{"evesso": []}],
                        "responses": {"200": {"description": "OK"}},
                        "x-compatibility-date": "2026-06-09",
                    }
                }
            },
        }
    )

    generated = generate_request_builders(
        schema=schema,
        package_name="generated_requests",
    )
    market_source = generated.files["market.py"]

    assert "auth_character_id: int," in market_source
    assert "auth_credential_id: UUID," in market_source
    assert "auth_character_id=auth_character_id" in market_source
    assert "auth_credential_id=auth_credential_id" in market_source
