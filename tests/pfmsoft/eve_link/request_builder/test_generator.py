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

    source = generate_request_builders(schema=schema, module_name="generated_requests")

    assert 'COMPATIBILITY_DATE: str = "2026-06-09"' in source
    assert "def get_markets_groups(" in source
    assert '"""Get a list of market groups.' in source
    assert "name: str | None = None" in source
    assert "accept_language: str | None = ACCEPT_LANGUAGE" in source
    assert "market_group_id: int" in source
    assert "page" not in source


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

    source = generate_request_builders(schema=schema, module_name="generated_requests")

    assert "x_compatibility_date: str | None = X_COMPATIBILITY_DATE" in source


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

    source = generate_request_builders(schema=schema, module_name="generated_requests")

    assert 'header_parameters["Accept-Language"] = accept_language' in source
    assert 'path_parameters["market_group_id"] = market_group_id' in source
    assert 'query_parameters["name"] = name' in source
    assert "header_parameters=header_parameters" in source
    assert "path_parameters=path_parameters" in source
    assert "query_parameters=query_parameters" in source


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

    source = generate_request_builders(
        schema=schema,
        module_name="generated_requests",
        exclude=frozenset({"name", "Accept-Language"}),
    )

    assert "name: str | None = None" not in source
    assert "accept_language" not in source
    assert "market_group_id: int" in source


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

    source = generate_request_builders(schema=schema, module_name="generated_requests")

    assert "def get_markets_groups(" in source
    assert (
        "request_body"
        not in source.split("def get_markets_groups(", 1)[1].split(
            "def post_markets_groups(", 1
        )[0]
    )
    assert "request_body: Any" in source
    assert "request_body: Any | None = None" not in source
    assert "request_body=request_body" in source
