"""Helpers for the CLI."""

import sys
from pathlib import Path
from typing import cast
from warnings import deprecated

import typer
from pfmsoft.api_request.settings import ApiRequestSettings
from pfmsoft.eve_auth_manager.settings import EveAuthManagerSettings
from pfmsoft.eve_snippets import save_text_file
from rich.console import Console

from pfmsoft.eve_link.schema.cache.schema_cache_disk import SchemaCacheManager
from pfmsoft.eve_link.schema.models import EsiSchema
from pfmsoft.eve_link.settings import SETTINGS_KEY, EsiLinkSettings


def get_stdin() -> str:
    """Read piped or redirected stdin content until EOF.

    Returns:
        Full stdin content as a string.

    Raises:
        ValueError: If stdin is attached to an interactive terminal instead
            of a pipe or redirected input source.
    """
    if sys.stdin.isatty():
        raise ValueError("Error: provide a file path or pipe data via stdin.")
    return sys.stdin.read()


def get_eve_link_settings_from_context(ctx: typer.Context) -> EsiLinkSettings:
    """Retrieve the Eve ESI Link settings from the Typer context.

    Args:
        ctx: The Typer context object.

    Returns:
        The Eve ESI Link settings.
    """
    settings = cast(EsiLinkSettings, ctx.obj.get(SETTINGS_KEY))
    return settings


@deprecated(
    "get_schema is deprecated, use the new schema management functions instead."
)
def get_schema(
    messenger: Console,
    schema_manager: SchemaCacheManager,
    compatibility_date: str | None,
) -> EsiSchema:
    """Get the EsiSchema from the cache."""
    try:
        if compatibility_date is not None:
            esi_schema = schema_manager.load(compatibility_date=compatibility_date)
        else:
            available_dates = schema_manager.list_entries()
            if not available_dates:
                messenger.print(
                    "[red]Error: No cached schemas found. Use --schema or update the cache.[/red]"
                )
                raise typer.Exit(code=1)
            most_recent_date = max(
                entry.compatibility_date for entry in available_dates
            )
            esi_schema = schema_manager.load(compatibility_date=most_recent_date)
            messenger.print(f"Using most recent cached schema: {most_recent_date}")
    except typer.Exit:
        raise
    except FileNotFoundError as e:
        messenger.print(
            f"[red]Error: No cached schema found for {compatibility_date}.[/red]"
        )
        raise typer.Exit(code=1) from e
    except Exception as e:
        messenger.print(f"[red]Error: Failed to load cached schema - {e}[/red]")
        raise typer.Exit(code=1) from e
    return esi_schema


def output_to_stdout_or_file(
    data_string: str,
    filepath: Path,
    overwrite: bool,
    messenger: Console,
) -> None:
    """Outputs the data to a file or stdout.

    Args:
        data_string: The string data to output.
        filepath: The path to the output file. If the filepath is Path("-"), output to stdout.
        overwrite: Whether to overwrite the file if it exists.
        messenger: The Console object for printing messages.

    Raises:
        FileExistsError: If the file already exists and overwrite is False.
    """
    if filepath == Path("-"):
        print(data_string)
    else:
        try:
            output_path = save_text_file(
                text=data_string,
                directory=filepath.parent,
                filename=filepath.name,
                overwrite=overwrite,
            )
        except FileExistsError as e:
            messenger.print(
                f"File {filepath} already exists. Use --overwrite to overwrite it."
            )
            raise e
        messenger.print(f"Output saved to {output_path}")
