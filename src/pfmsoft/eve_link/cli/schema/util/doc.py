"""Generate markdown documentation from a serialized EsiSchema JSON payload."""

from pathlib import Path
from typing import Annotated

import typer
from pfmsoft.eve_snippets import save_text_file
from rich.console import Console
from rich.markdown import Markdown

from pfmsoft.eve_link.cli.helpers import get_stdin
from pfmsoft.eve_link.schema.models import EsiSchema
from pfmsoft.eve_link.schema.schema_report import generate_esi_schema_markdown_report

app = typer.Typer(no_args_is_help=True)


@app.command(
    name="generate-doc",
    help="Generate operation-focused markdown docs from an EsiSchema JSON file or stdin stream.",
)
def generate_schema_doc(
    file_in: Annotated[
        Path | None,
        typer.Option(
            "--from",
            file_okay=True,
            dir_okay=False,
            readable=True,
            allow_dash=True,
            help="Path to a serialized EsiSchema JSON file. Use - to read from stdin.",
        ),
    ] = None,
    file_out: Annotated[
        Path,
        typer.Option(
            "--to",
            help="Output markdown file path. Use - for stdout.",
            allow_dash=True,
            dir_okay=False,
        ),
    ] = Path("-"),
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite output file if it already exists.",
        ),
    ] = False,
    plain: Annotated[
        bool,
        typer.Option(
            "--plain",
            help="Display the output in plain text instead of Rich Markdown.",
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
    """Generate markdown documentation from a serialized EsiSchema JSON payload.

    The input schema must already be a downloaded ESI schema document. Supply it via
    --from path/to/schema.json or pipe it via stdin with --from -.

    The generated markdown includes version metadata, TOC grouped by tag, and a
    per-operation section that covers summary, parameters, request body, response schema,
    and extension fields.
    """
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)
    if file_in is None:
        messenger.print(
            "[red]Error: A schema source is required. Use --from <path> or --from - for stdin.[/red]"
        )
        raise typer.Exit(code=1)

    if file_in == Path("-"):
        try:
            input_data = get_stdin()
            esi_schema = EsiSchema.deserialize(input_data)
        except Exception as e:
            messenger.print(
                f"[red]Error: Failed to load schema from JSON input - {e}[/red]"
            )
            raise typer.Exit(code=1) from e
    else:
        try:
            esi_schema = EsiSchema.deserialize(file_in.read_text(encoding="utf-8"))
        except Exception as e:
            messenger.print(f"[red]Error: Failed to read input file - {e}[/red]")
            raise typer.Exit(code=1) from e

    markdown_doc = generate_esi_schema_markdown_report(schema=esi_schema)
    if file_out == Path("-"):
        if plain:
            print(markdown_doc)
        else:
            messenger.print(Markdown(markdown_doc))
        raise typer.Exit()

    if file_out.suffix == ".md":
        file_path = file_out
    else:
        schema_compat_date = esi_schema.compatibility_date
        default_file_name = f"schema_docs_{schema_compat_date}.md"
        file_path = file_out / default_file_name
    try:
        output_path = save_text_file(
            text=markdown_doc,
            directory=file_path.parent,
            filename=file_path.name,
            overwrite=overwrite,
        )
    except Exception as e:
        messenger.print(f"[red]Error: Failed to save output file - {e}[/red]")
        raise typer.Exit(code=1) from e
    messenger.print(f"[green]Markdown documentation saved to {output_path}[/green]")
