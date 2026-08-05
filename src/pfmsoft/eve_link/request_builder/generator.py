"""Core logic for generating request builder modules from ESI schemas."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from pfmsoft.eve_link.schema.models import EsiSchema

EXCLUDED = frozenset({"page", "If-None-Match", "If-Modified-Since"})


@dataclass(slots=True, kw_only=True)
class ParameterContext:
    """Template context for a generated function parameter."""

    argument_name: str
    schema_name: str
    required: bool
    kind: str
    type_hint: str
    default: str | None
    has_default: bool


@dataclass(slots=True, kw_only=True)
class OperationContext:
    """Template context for a generated request builder operation."""

    operation_id: str
    function_name: str
    description: str
    parameters: list[ParameterContext] = field(default_factory=list[ParameterContext])
    has_request_body: bool = False
    requires_authentication: bool = False


@dataclass(slots=True, kw_only=True)
class TagContext:
    """Template context for a group of generated request builders."""

    name: str
    module_name: str
    operations: list[OperationContext] = field(default_factory=list[OperationContext])


@dataclass(slots=True, kw_only=True)
class TemplateContext:
    """Top-level template context for generated output."""

    module_name: str
    compatibility_date: str
    tags: list[TagContext] = field(default_factory=list[TagContext])


@dataclass(slots=True, kw_only=True)
class GeneratedPackage:
    """Generated package files keyed by path relative to the package root."""

    package_name: str
    files: dict[str, str] = field(default_factory=dict[str, str])


def generate_request_builders(
    *,
    schema: EsiSchema,
    package_name: str = "request_factory",
    exclude: frozenset[str] | None = EXCLUDED,
) -> GeneratedPackage:
    """Render request builder package files for the provided schema.

    Args:
        schema: The ESI schema used to derive the request builders.
        package_name: The Python package name for the generated package.
        exclude: Parameter names to omit from the generated function signatures.

    Returns:
        Generated package files keyed by relative path.
    """
    env = Environment(
        loader=PackageLoader("pfmsoft.eve_link.request_builder"),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
    )
    init_template = env.get_template("package_init.py.j2")
    tag_template = env.get_template("tag_module.py.j2")

    operations_by_tag: dict[str, list[OperationContext]] = {}
    for operation_id, operation in schema.operations.items():
        tag = operation.tags[0] if operation.tags else "General"
        operations_by_tag.setdefault(tag, []).append(
            OperationContext(
                operation_id=operation_id,
                function_name=_to_snake_case(operation_id),
                description=_sanitize_description(operation.description),
                parameters=_build_parameters(
                    operation,
                    exclude=exclude or frozenset(),
                ),
                has_request_body=operation.request_body is not None,
                requires_authentication=operation.is_authentication_required,
            )
        )

    for operations in operations_by_tag.values():
        operations.sort(key=lambda item: item.function_name)

    tags: list[TagContext] = []
    used_module_names: set[str] = set()
    for tag, operations in sorted(operations_by_tag.items()):
        module_name_for_tag = _to_unique_module_name(tag, used=used_module_names)
        tags.append(
            TagContext(
                name=tag,
                module_name=module_name_for_tag,
                operations=operations,
            )
        )

    context = TemplateContext(
        module_name=package_name,
        compatibility_date=schema.compatibility_date,
        tags=tags,
    )
    rendered_context = asdict(context)

    files: dict[str, str] = {
        "__init__.py": init_template.render(rendered_context),
    }
    for tag in context.tags:
        files[f"{tag.module_name}.py"] = tag_template.render(asdict(tag))

    return GeneratedPackage(package_name=package_name, files=files)


def _to_snake_case(value: str) -> str:
    """Convert an operation ID to a snake_case function name."""
    parts: list[str] = []
    current: list[str] = []
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


def _to_unique_module_name(tag: str, *, used: set[str]) -> str:
    """Convert a tag value to a unique snake_case Python module name."""
    normalized = re.sub(r"[^a-z0-9]+", "_", tag.strip().lower()).strip("_")
    base_name = normalized or "general"

    module_name = base_name
    suffix = 2
    while module_name in used:
        module_name = f"{base_name}_{suffix}"
        suffix += 1
    used.add(module_name)
    return module_name


def _build_parameters(
    operation: Any,
    *,
    exclude: frozenset[str],
) -> list[ParameterContext]:
    """Build parameter metadata for the render context."""
    parameters: list[ParameterContext] = []
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
        parameters.append(
            ParameterContext(
                argument_name=_to_parameter_name(name),
                schema_name=name,
                required=bool(param.get("required", False)),
                kind=location,
                type_hint=_parameter_type_hint(param),
                default=default,
                has_default=default is not None,
            )
        )
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
