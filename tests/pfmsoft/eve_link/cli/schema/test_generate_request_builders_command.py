"""Tests for schema request-builder generation CLI command."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from pfmsoft.eve_link.cli.schema.util import generate_request_builders as command
from pfmsoft.eve_link.request_builder import GeneratedPackage

runner = CliRunner()


def test_generate_request_builders_writes_package_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Write a generated request-builder package to the output directory."""
    input_path = tmp_path / "schema.json"
    input_path.write_text("{}", encoding="utf-8")
    output_dir = tmp_path / "generated_requests"

    monkeypatch.setattr(
        command,
        "get_eve_link_settings_from_context",
        lambda _ctx: SimpleNamespace(),
    )
    monkeypatch.setattr(command, "SimpleRequests", lambda settings: SimpleNamespace())
    monkeypatch.setattr(
        command, "load_esi_schema_from_file", lambda **_kwargs: object()
    )
    monkeypatch.setattr(
        command,
        "generate_request_builders",
        lambda **_kwargs: GeneratedPackage(
            package_name="generated_requests",
            files={
                "__init__.py": "X_COMPATIBILITY_DATE = '2026-06-09'\n",
                "market.py": "from . import X_COMPATIBILITY_DATE\n",
            },
        ),
    )

    result = runner.invoke(
        command.app,
        ["--from", str(input_path), "--to", str(output_dir)],
    )

    assert result.exit_code == 0
    assert (output_dir / "__init__.py").read_text(encoding="utf-8")
    assert (output_dir / "market.py").read_text(encoding="utf-8")
    assert "Request builders saved to" in result.stderr


def test_generate_request_builders_rejects_stdout_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Return a user-facing error when package output path is stdout."""
    input_path = tmp_path / "schema.json"
    input_path.write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        command,
        "get_eve_link_settings_from_context",
        lambda _ctx: SimpleNamespace(),
    )
    monkeypatch.setattr(command, "SimpleRequests", lambda settings: SimpleNamespace())
    monkeypatch.setattr(
        command, "load_esi_schema_from_file", lambda **_kwargs: object()
    )
    monkeypatch.setattr(
        command,
        "generate_request_builders",
        lambda **_kwargs: GeneratedPackage(package_name="generated_requests", files={}),
    )

    result = runner.invoke(command.app, ["--from", str(input_path), "--to", "-"])

    assert result.exit_code == 1
    assert "Package output requires a directory path for --to" in result.stderr


def test_generate_request_builders_uses_package_name_option(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Pass --package-name through to generator package_name argument."""
    input_path = tmp_path / "schema.json"
    input_path.write_text("{}", encoding="utf-8")
    output_dir = tmp_path / "generated_requests"
    captured_kwargs: dict[str, object] = {}

    monkeypatch.setattr(
        command,
        "get_eve_link_settings_from_context",
        lambda _ctx: SimpleNamespace(),
    )
    monkeypatch.setattr(command, "SimpleRequests", lambda settings: SimpleNamespace())
    monkeypatch.setattr(
        command, "load_esi_schema_from_file", lambda **_kwargs: object()
    )

    def _fake_generate_request_builders(**kwargs: object) -> GeneratedPackage:
        captured_kwargs.update(kwargs)
        return GeneratedPackage(package_name="custom_pkg", files={"__init__.py": ""})

    monkeypatch.setattr(
        command, "generate_request_builders", _fake_generate_request_builders
    )

    result = runner.invoke(
        command.app,
        [
            "--from",
            str(input_path),
            "--to",
            str(output_dir),
            "--package-name",
            "custom_pkg",
        ],
    )

    assert result.exit_code == 0
    assert captured_kwargs["package_name"] == "custom_pkg"
