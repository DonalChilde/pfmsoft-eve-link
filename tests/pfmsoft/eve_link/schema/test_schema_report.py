"""Tests for Jinja-based schema report generation."""

from __future__ import annotations

from pfmsoft.eve_link.schema.helpers.schema_files import load_esi_schema
from pfmsoft.eve_link.schema.schema_report import generate_esi_schema_markdown_report


def _build_schema_dict(*, include_timestamp: bool = True) -> dict[str, object]:
    """Build a compact schema payload for report tests."""
    schema = {
        "openapi": "3.0.0",
        "info": {"version": "2026-08-10", "title": "test-schema"},
        "servers": [{"url": "https://esi.evetech.net"}],
        "paths": {
            "/status/": {
                "get": {
                    "operationId": "GetStatus",
                    "tags": ["Status"],
                    "description": "Get current status",
                    "summary": "Current server status",
                    "parameters": [
                        {
                            "name": "datasource",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Datasource.",
                        }
                    ],
                    "x-compatibility-date": "2026-08-10",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"status": {"type": "string"}},
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/routes/": {
                "post": {
                    "operationId": "CreateRoute",
                    "description": "",
                    "tags": [],
                    "responses": {},
                    "x-compatibility-date": "2026-08-10",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {"start": {"type": "integer"}},
                                }
                            }
                        }
                    },
                    "x-rate-limit": {"burst": 20, "remain": 10},
                }
            },
        },
        "components": {"schemas": {}},
    }
    if include_timestamp:
        return {"schema": schema, "timestamp": 1723290000000000000}
    return schema


def test_generate_schema_report_includes_expected_sections() -> None:
    """Render report content with expected operation sections and headings."""
    esi_schema = load_esi_schema(_build_schema_dict())

    report = generate_esi_schema_markdown_report(esi_schema)

    assert "# ESI Schema Documentation" in report
    assert "## Table of Contents" in report
    assert "## Tag: Status" in report
    assert "## Tag: untagged" in report
    assert "### GetStatus" in report
    assert "### CreateRoute" in report
    assert "#### Request Body (json_payload) Schema" in report
    assert "#### Response Schema" in report


def test_generate_schema_report_uses_unknown_date_without_timestamp() -> None:
    """Render Unknown download date when schema timestamp is absent."""
    esi_schema = load_esi_schema(_build_schema_dict(include_timestamp=False))

    report = generate_esi_schema_markdown_report(esi_schema)

    assert "Download Date" in report
    assert ": Unknown" in report


def test_generate_schema_report_uses_json_fenced_blocks_only() -> None:
    """Render JSON fenced blocks in report sections."""
    esi_schema = load_esi_schema(_build_schema_dict())

    report = generate_esi_schema_markdown_report(esi_schema)

    assert "```json" in report
    assert "```yaml" not in report


def test_generate_schema_report_is_deterministic() -> None:
    """Render stable markdown across repeated calls for same schema."""
    esi_schema = load_esi_schema(_build_schema_dict())

    first = generate_esi_schema_markdown_report(esi_schema)
    second = generate_esi_schema_markdown_report(esi_schema)

    assert first == second
