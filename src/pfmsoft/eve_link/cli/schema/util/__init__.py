"""Utility commands for schema fetch, generation, and documentation."""

import typer

app = typer.Typer(
    no_args_is_help=True,
    name="util",
    help="Utility commands for schema fetches, generation, and docs.",
)

from .doc import app as generate_doc_app
from .fetch import app as fetch_schema_app
from .fetch_changelog import app as fetch_changelog_app
from .fetch_dates import app as fetch_dates_app
from .generate_request_builders import app as generate_request_builders_app

app.add_typer(fetch_schema_app)
app.add_typer(fetch_dates_app)
app.add_typer(generate_doc_app)
app.add_typer(fetch_changelog_app)
app.add_typer(generate_request_builders_app)
