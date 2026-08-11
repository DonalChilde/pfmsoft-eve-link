"""Schema CLI command group."""

import typer

app = typer.Typer(
    no_args_is_help=True,
    name="schema",
    help="Commands for fetching and working with ESI schemas.",
)

from .cache import app as cache_app
from .util import app as util_app

app.add_typer(util_app)
app.add_typer(cache_app)
