"""Generate markdown schema reports using Jinja templates.

This module provides a new report-generation path that composes markdown from
Jinja templates and dataclass-based render context objects.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader
from mdformat import text as mdformat_text  # type: ignore

from pfmsoft.eve_link.schema.models import EsiSchema, SchemaOperation


@dataclass(slots=True, kw_only=True)
class TocOperationContext:
    """Template context for one operation link in the TOC."""

    operation_id: str
    operation_anchor: str


@dataclass(slots=True, kw_only=True)
class SummaryRowContext:
    """Template context for one summary table row."""

    field_name: str
    value: str


@dataclass(slots=True, kw_only=True)
class ParameterRowContext:
    """Template context for one parameter table row."""

    name: str
    parameter_in: str
    required: str
    parameter_type: str
    description: str


@dataclass(slots=True, kw_only=True)
class TocTagContext:
    """Template context for one tag group in the TOC."""

    tag_name: str
    tag_anchor: str
    operations: list[TocOperationContext] = field(
        default_factory=list[TocOperationContext]
    )


@dataclass(slots=True, kw_only=True)
class OperationSectionContext:
    """Template context for one operation report section."""

    operation_id: str
    description: str
    summary_rows: list[SummaryRowContext] = field(
        default_factory=list[SummaryRowContext]
    )
    parameter_rows: list[ParameterRowContext] = field(
        default_factory=list[ParameterRowContext]
    )
    parameters_schema_md: str
    request_body_schema_md: str
    response_schema_md: str
    extensions_schema_md: str | None = None


@dataclass(slots=True, kw_only=True)
class TagSectionContext:
    """Template context for one tag report section."""

    tag_name: str
    tag_anchor: str
    operations: list[OperationSectionContext] = field(
        default_factory=list[OperationSectionContext]
    )


@dataclass(slots=True, kw_only=True)
class ReportContext:
    """Top-level template context for the schema markdown report."""

    version: str
    download_date_display: str
    server_url: str
    toc_tags: list[TocTagContext] = field(default_factory=list[TocTagContext])
    tags: list[TagSectionContext] = field(default_factory=list[TagSectionContext])


def _render_json_fenced_block(data: Any) -> str:
    """Render a value inside a JSON markdown fenced code block."""
    body = json.dumps(data, indent=2, sort_keys=False)
    return f"```json\n{body}\n```"


def _resolve_download_date_display(schema: EsiSchema) -> str:
    """Resolve a displayable download date from schema timestamp."""
    if schema.timestamp is None:
        return "Unknown"
    return schema.timestamp


def _slugify_heading(value: str) -> str:
    """Create predictable markdown heading anchors."""
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
    normalized = re.sub(r"[\s-]+", "-", normalized)
    return normalized.strip("-")


def _group_operations_by_tag(
    operations: dict[str, SchemaOperation],
) -> dict[str, list[SchemaOperation]]:
    """Group operations by tag, preserving deterministic sorting."""
    grouped: dict[str, list[SchemaOperation]] = defaultdict(list)
    for operation in operations.values():
        tags = operation.tags or ["untagged"]
        for tag in tags:
            grouped[tag].append(operation)
    return {
        tag: sorted(ops, key=lambda item: item.operation_id)
        for tag, ops in sorted(grouped.items(), key=lambda item: item[0])
    }


def _parameter_type(parameter: dict[str, Any]) -> str:
    """Extract parameter type for table display."""
    schema = parameter.get("schema", {})
    return str(schema.get("type", "-"))


def _parameter_description(parameter: dict[str, Any]) -> str:
    """Extract parameter description with schema-level fallback."""
    top_level_description = parameter.get("description")
    if isinstance(top_level_description, str) and top_level_description.strip():
        return top_level_description.replace("\n", " ")

    schema = parameter.get("schema", {})
    schema_description = schema.get("description")
    if isinstance(schema_description, str) and schema_description.strip():
        return schema_description.replace("\n", " ")

    return "-"


def _table_cell(value: Any) -> str:
    """Sanitize values for markdown table cells."""
    normalized = str(value).replace("\n", " ")
    # Escape literal pipes so markdown table columns remain stable.
    return normalized.replace("|", "\\|")


def _build_summary_rows(operation: SchemaOperation) -> list[SummaryRowContext]:
    """Build summary table rows for a single operation."""
    response_keys = (
        ", ".join(operation.response_keys) if operation.response_keys else "-"
    )
    try:
        compatibility_date = operation.compatibility_date
    except ValueError:
        compatibility_date = "-"

    rows = [
        SummaryRowContext(
            field_name="Operation ID",
            value=_table_cell(operation.operation_id),
        ),
        SummaryRowContext(
            field_name="Method",
            value=_table_cell(str(operation.method)),
        ),
        SummaryRowContext(
            field_name="Path",
            value=_table_cell(operation.path),
        ),
        SummaryRowContext(
            field_name="Authorization Required",
            value="Yes" if operation.is_authentication_required else "No",
        ),
        SummaryRowContext(
            field_name="Compatibility Date",
            value=_table_cell(compatibility_date),
        ),
        SummaryRowContext(
            field_name="Response Keys",
            value=_table_cell(response_keys),
        ),
        SummaryRowContext(
            field_name="Summary",
            value=_table_cell(operation.summary or "-"),
        ),
    ]
    return rows


def _build_parameter_rows(operation: SchemaOperation) -> list[ParameterRowContext]:
    """Build path/query/header parameter table rows."""
    parameters = [
        *operation.path_and_query_parameters,
        *operation.header_params,
    ]
    rows: list[ParameterRowContext] = []
    for parameter in parameters:
        rows.append(
            ParameterRowContext(
                name=_table_cell(parameter.get("name", "-")),
                parameter_in=_table_cell(parameter.get("in", "-")),
                required="Yes" if parameter.get("required", False) else "No",
                parameter_type=_table_cell(_parameter_type(parameter)),
                description=_table_cell(_parameter_description(parameter)),
            )
        )
    return rows


def _render_parameters_schema(operation: SchemaOperation) -> str:
    """Render path/query/header parameters as a fenced schema block."""
    parameters = [
        *operation.path_and_query_parameters,
        *operation.header_params,
    ]
    if not parameters:
        return "No Parameters Schema."
    return _render_json_fenced_block(parameters)


def _build_operation_section_context(
    operation: SchemaOperation,
) -> OperationSectionContext:
    """Build an operation section template context."""
    request_body_schema_md = (
        "No Request Body Schema."
        if operation.request_body is None
        else _render_json_fenced_block(operation.request_body)
    )
    response_schema_md = (
        _render_json_fenced_block(operation.responses_200)
        if operation.responses_200
        else "No 200 application/json response schema."
    )

    extensions_schema_md: str | None = None
    if operation.x_values:
        extension_dict: dict[str, Any] = {}
        for entry in operation.x_values:
            extension_dict.update(entry)
        extensions_schema_md = _render_json_fenced_block(extension_dict)

    return OperationSectionContext(
        operation_id=operation.operation_id,
        description=operation.description.replace("\n", " ") or "No description.",
        summary_rows=_build_summary_rows(operation),
        parameter_rows=_build_parameter_rows(operation),
        parameters_schema_md=_render_parameters_schema(operation),
        request_body_schema_md=request_body_schema_md,
        response_schema_md=response_schema_md,
        extensions_schema_md=extensions_schema_md,
    )


def _build_report_context(schema: EsiSchema) -> ReportContext:
    """Build top-level template context from a schema model."""
    grouped_operations = _group_operations_by_tag(schema.operations)

    toc_tags: list[TocTagContext] = []
    tags: list[TagSectionContext] = []

    for tag_name, operations in grouped_operations.items():
        tag_anchor = _slugify_heading(f"Tag: {tag_name}")
        toc_operations = [
            TocOperationContext(
                operation_id=operation.operation_id,
                operation_anchor=_slugify_heading(operation.operation_id),
            )
            for operation in operations
        ]
        toc_tags.append(
            TocTagContext(
                tag_name=tag_name,
                tag_anchor=tag_anchor,
                operations=toc_operations,
            )
        )
        tags.append(
            TagSectionContext(
                tag_name=tag_name,
                tag_anchor=tag_anchor,
                operations=[
                    _build_operation_section_context(operation)
                    for operation in operations
                ],
            )
        )

    return ReportContext(
        version=schema.version,
        download_date_display=_resolve_download_date_display(schema),
        server_url=schema.base_url,
        toc_tags=toc_tags,
        tags=tags,
    )


def generate_esi_schema_markdown_report(schema: EsiSchema) -> str:
    """Generate an operation-focused markdown report for an ESI schema.

    Args:
        schema: ESI schema model.

    Returns:
        Rendered and mdformat-normalized markdown report.
    """
    env = Environment(
        loader=PackageLoader("pfmsoft.eve_link.templates", "schema_report"),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    root_template = env.get_template("report.md.j2")
    context = _build_report_context(schema)
    rendered = root_template.render(report=context)
    return mdformat_text(rendered, extensions=["tables"])


def _build_parser() -> argparse.ArgumentParser:
    """Build argument parser for standalone report generation."""
    parser = argparse.ArgumentParser(
        description="Generate markdown schema report from a schema JSON file."
    )
    parser.add_argument(
        "--from", dest="file_in", required=True, help="Input schema JSON path."
    )
    parser.add_argument(
        "--to", dest="file_out", required=True, help="Output markdown file path."
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite output file if it already exists.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run standalone report generation from command-line arguments."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    file_in = Path(args.file_in)
    file_out = Path(args.file_out)

    try:
        schema = EsiSchema.deserialize(file_in.read_text(encoding="utf-8"))
        report = generate_esi_schema_markdown_report(schema)

        if file_out.exists() and not args.overwrite:
            print(
                f"Error: Output file already exists: {file_out}. Use --overwrite.",
                file=sys.stderr,
            )
            return 1

        file_out.parent.mkdir(parents=True, exist_ok=True)
        file_out.write_text(report, encoding="utf-8")
    except Exception as e:
        print(f"Error: Failed to generate schema report - {e}", file=sys.stderr)
        return 1

    print(f"Schema report saved to {file_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
