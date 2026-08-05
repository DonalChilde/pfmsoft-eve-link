"""Core logic for generating request builder modules from ESI schemas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pfmsoft.eve_link.schema.models import EsiSchema

_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

EXCLUDED = frozenset({"page", "If-None-Match", "If-Modified-Since"})


def generate_request_builders(
    *,
    schema: EsiSchema,
    module_name: str,
    exclude: frozenset[str] | None = EXCLUDED,
) -> str:
    """Render a request builder module for the provided schema.

    Args:
        schema: The ESI schema used to derive the request builders.
        module_name: The Python module name for the generated module.
        exclude: Parameter names to omit from the generated function signatures.

    Returns:
        The rendered Python source code.
    """
    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
    )
    template = env.get_template("module.py.j2")

    operations_by_tag: dict[str, list[dict[str, Any]]] = {}
    for operation_id, operation in schema.operations.items():
        tag = operation.tags[0] if operation.tags else "General"
        operations_by_tag.setdefault(tag, []).append({
            "operation_id": operation_id,
            "function_name": _to_snake_case(operation_id),
            "description": _sanitize_description(operation.description),
            "parameters": _build_parameters(
                operation,
                exclude=exclude or frozenset(),
            ),
            "has_request_body": operation.request_body is not None,
            "requires_authentication": operation.is_authentication_required,
            "compatibility_date": schema.compatibility_date,
        })

    for operations in operations_by_tag.values():
        operations.sort(key=lambda item: item["function_name"])

    context = {
        "module_name": module_name,
        "compatibility_date": schema.compatibility_date,
        "tags": [
            {"name": tag, "operations": ops}
            for tag, ops in sorted(operations_by_tag.items())
        ],
    }
    return template.render(context)


def _to_snake_case(value: str) -> str:
    """Convert an operation ID to a snake_case function name."""
    parts = []
    current = []
    for char in value:
        if char.isupper() and current:
            parts.append("".join(current))
            current = [char.lower()]
        else:
            current.append(char.lower())
    if current:
        parts.append("".join(current))
    return "_".join(part for part in parts if part)


def _sanitize_description(value: str) -> str:
    """Normalize a schema description for use in a docstring."""
    normalized = " ".join(value.replace("\n", " ").split())
    if not normalized:
        return "Generated request builder."
    if normalized[-1] not in {".", "!", "?"}:
        return f"{normalized}."
    return normalized


def _build_parameters(
    operation: Any,
    *,
    exclude: frozenset[str],
) -> list[dict[str, Any]]:
    """Build parameter metadata for the render context."""
    parameters: list[dict[str, Any]] = []
    for param in (
        operation.path_parameters + operation.query_parameters + operation.header_params
    ):
        name = str(param["name"])
        location = str(param["in"])
        if name in exclude:
            continue
        if name == "page":
            continue
        default = _parameter_default(
            name, location, required=bool(param.get("required", False))
        )
        parameters.append({
            "argument_name": _to_parameter_name(name),
            "schema_name": name,
            "required": bool(param.get("required", False)),
            "kind": location,
            "type_hint": _parameter_type_hint(param),
            "default": default,
            "has_default": default is not None,
        })
    return parameters


def _to_parameter_name(value: str) -> str:
    """Convert a parameter name to a valid Python identifier."""
    normalized = value.strip().replace("-", "_")
    if not normalized:
        return "parameter"
    return normalized.lower()


def _parameter_default(name: str, location: str, *, required: bool) -> str | None:
    """Return the default expression for a parameter.

    Optional parameters should default to ``None``. Known header defaults should also be
    rendered even when the schema marks them as required so the generated signatures stay
    informative.
    """
    if location == "header":
        if name.lower() == "accept-language":
            return "ACCEPT_LANGUAGE"
        if name.lower() == "x-tenant":
            return "X_TENANT"
        if name.lower() == "x-compatibility-date":
            return "X_COMPATIBILITY_DATE"
    if not required:
        return "None"
    return None


def _parameter_type_hint(param: dict[str, Any]) -> str:
    """Infer a simple type hint from parameter schema metadata."""
    schema = param.get("schema", {})
    if schema.get("type") == "integer":
        return "int"
    if schema.get("type") == "number":
        return "float"
    if schema.get("type") == "boolean":
        return "bool"
    return "str"
