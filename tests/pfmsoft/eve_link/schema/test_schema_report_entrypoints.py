"""Tests for schema report module argparse entrypoints."""

from __future__ import annotations

from pathlib import Path

from pfmsoft.eve_link.schema import schema_report
from pfmsoft.eve_link.schema.models import EsiSchema


def _write_schema_json(path: Path) -> None:
    """Write a serialized EsiSchema payload for entrypoint tests."""
    raw_schema = {
        "openapi": "3.0.0",
        "info": {"version": "2026-08-10", "title": "test-schema"},
        "servers": [{"url": "https://esi.evetech.net"}],
        "paths": {
            "/status/": {
                "get": {
                    "operationId": "GetStatus",
                    "tags": ["Status"],
                    "description": "Get status",
                    "x-compatibility-date": "2026-08-10",
                    "responses": {
                        "200": {
                            "description": "ok",
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        }
                    },
                }
            }
        },
        "components": {"schemas": {}},
    }
    serialized = EsiSchema.from_raw_schema(
        raw_schema,
        timestamp=1723290000000000000,
    ).serialize()
    path.write_text(serialized, encoding="utf-8")


def test_schema_report_main_writes_file(tmp_path: Path) -> None:
    """Generate markdown from schema_report main entrypoint."""
    file_in = tmp_path / "schema.json"
    file_out = tmp_path / "schema_report.md"
    _write_schema_json(file_in)

    code = schema_report.main([
        "--from",
        str(file_in),
        "--to",
        str(file_out),
    ])

    assert code == 0
    assert file_out.exists()
    assert "# ESI Schema Documentation" in file_out.read_text(encoding="utf-8")


def test_schema_report_main_honors_overwrite_guard(tmp_path: Path) -> None:
    """Refuse to overwrite existing output unless overwrite is enabled."""
    file_in = tmp_path / "schema.json"
    file_out = tmp_path / "schema_report.md"
    _write_schema_json(file_in)
    file_out.write_text("existing", encoding="utf-8")

    code = schema_report.main(["--from", str(file_in), "--to", str(file_out)])

    assert code == 1
