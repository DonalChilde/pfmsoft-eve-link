"""Generate Python request builder modules from an ESI schema."""

from pathlib import Path
from typing import Annotated

import typer
from pfmsoft.eve_snippets import json_io
from rich.console import Console

from pfmsoft.eve_link.cli.helpers import (
    get_eve_link_settings_from_context,
    get_stdin,
)
from pfmsoft.eve_link.esi_link import SimpleRequests
from pfmsoft.eve_link.request_builder import generate_request_builders
from pfmsoft.eve_link.schema.helpers.schema_files import (
    load_esi_schema,
    load_esi_schema_from_file,
)

app = typer.Typer(no_args_is_help=True)


@app.command(
    name="generate-request-builders",
    help="Generate Python request builder modules from an ESI schema.",
)
def generate_request_builders_command(
    ctx: typer.Context,
    file_in: Annotated[
        Path | None,
        typer.Option(
            "--from",
            file_okay=True,
            dir_okay=False,
            readable=True,
            allow_dash=True,
            help="Path to schema JSON. Use - for stdin. Defaults to the cached schema from --date.",
        ),
    ] = None,
    compatibility_date: Annotated[
        str | None,
        typer.Option(
            "--date",
            show_default=True,
            help="Compatibility date (YYYY-MM-DD) of cached ESI schema to use.",
        ),
    ] = None,
    directory_out: Annotated[
        Path,
        typer.Option(
            "--to",
            help="Output directory path for the generated package.",
            allow_dash=True,
        ),
    ] = Path("-"),
    package_name: Annotated[
        str,
        typer.Option(
            "--package-name",
            help="Python package name to use in the generated output.",
        ),
    ] = "generated_requests",
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite output file if it already exists.",
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Suppress status output.",
        ),
    ] = False,
) -> None:
    """Generate Python request builder functions from an ESI schema package."""
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    settings = get_eve_link_settings_from_context(ctx)
    simple_requests = SimpleRequests(settings=settings)

    if file_in == Path("-"):
        input_data = get_stdin()
        try:
            schema_dict = json_io.json_loads(input_data)
        except Exception as e:
            messenger.print(f"[red]Error: Failed to parse JSON input - {e}[/red]")
            raise typer.Exit(code=1) from e
        try:
            esi_schema = load_esi_schema(schema_dict)
        except Exception as e:
            messenger.print(
                f"[red]Error: Failed to load schema from JSON input - {e}[/red]"
            )
            raise typer.Exit(code=1) from e
    elif file_in is not None:
        try:
            esi_schema = load_esi_schema_from_file(file_path=file_in)
        except Exception as e:
            messenger.print(f"[red]Error: Failed to read input file - {e}[/red]")
            raise typer.Exit(code=1) from e
    else:
        esi_schema = simple_requests.get_schema(compatibility_date=compatibility_date)

    generated_package = generate_request_builders(
        schema=esi_schema,
        package_name=package_name,
    )
    if directory_out == Path("-"):
        messenger.print(
            "[red]Error: Package output requires a directory path for --to.[/red]"
        )
        raise typer.Exit(code=1)

    package_root = directory_out
    if directory_out.suffix == ".py":
        package_root = directory_out.parent / directory_out.stem

    try:
        if package_root.exists() and not package_root.is_dir():
            raise ValueError(f"Output path is not a directory: {package_root}")

        existing_files = [
            package_root / relative_path
            for relative_path in generated_package.files
            if (package_root / relative_path).exists()
        ]
        if existing_files and not overwrite:
            file_list = ", ".join(str(path.name) for path in sorted(existing_files))
            raise FileExistsError(
                f"File(s) already exist in output package: {file_list}. "
                "Use --overwrite to replace them."
            )

        package_root.mkdir(parents=True, exist_ok=True)
        for relative_path, source in generated_package.files.items():
            output_file = package_root / relative_path
            output_file.write_text(source, encoding="utf-8")
    except Exception as e:
        messenger.print(f"[red]Error: Failed to save output package - {e}[/red]")
        raise typer.Exit(code=1) from e

    messenger.print(f"[green]Request builders saved to {package_root}[/green]")
