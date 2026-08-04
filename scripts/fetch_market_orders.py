# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pfmsoft-eve-link>=0.4.1",
#     "typer>=0.26.8",
# ]
# [tool.uv.sources]
# pfmsoft-eve-link = { git = "https://github.com/DonalChilde/pfmsoft-eve-link.git", branch = "dev" }
# ///

####################################################################################################
# run with `uv run <script>`
# Add this to the script config header to use the dev branch of pfmsoft-eve-link:
# [tool.uv.sources]
# pfmsoft-eve-link = { git = "https://github.com/DonalChilde/pfmsoft-eve-link.git", branch = "dev" }
####################################################################################################

"""This script fetches market orders for a given region ID from the EVE Online API and saves them to a file or prints them to stdout."""

import asyncio
from pathlib import Path
from typing import Annotated, TypedDict, cast
from uuid import uuid4

import typer
from pfmsoft.eve_snippets import json_io, save_text_file
from whenever import Instant

from pfmsoft.eve_link import EsiRequest, SimpleRequests
from pfmsoft.eve_link.esi_request.models import EsiResponse, FailedEsiResponse
from pfmsoft.eve_link.settings import get_settings

app = typer.Typer(no_args_is_help=True)


class DividedOrders(TypedDict):
    buy_orders: list[MarketOrderTD]
    sell_orders: list[MarketOrderTD]


class MarketOrderTD(TypedDict):
    """TypedDict for market orders response."""

    duration: int
    is_buy_order: bool
    issued: str
    location_id: int
    min_volume: int
    order_id: int
    price: float
    range: str
    system_id: int
    type_id: int
    volume_remain: int
    volume_total: int


TypeId = int
OrdersDict = dict[TypeId, DividedOrders]  # type_id -> DividedOrders


class MarketOrdersResponse(TypedDict):
    region_id: int
    """The region ID for which the market orders were fetched."""
    timestamp_iso: str
    """The timestamp when the market orders were fetched."""
    expires_at: str | None
    """The timestamp when the market orders will expire, if provided by the ESI response."""
    orders: OrdersDict
    """The market orders divided by type ID and buy/sell orders."""


@app.command()
def main(
    region_id: Annotated[
        int,
        typer.Option("--region-id", help="The region ID to fetch market orders for"),
    ],
    output_directory: Annotated[
        Path,
        typer.Option(
            "--to",
            help="Path to the directory where the market orders will be saved. Use '-' "
            "to print to stdout.",
            exists=False,
            file_okay=False,
            dir_okay=True,
            show_default=True,
        ),
    ] = Path("-"),
    filename: Annotated[
        str | None,
        typer.Option(
            "--filename",
            help="Name of the file to save the market orders to. If not given, a default "
            "filename will be generated. Ignored if output directory is '-'",
            show_default=True,
        ),
    ] = None,
    indent: Annotated[
        int,
        typer.Option(
            "--indent",
            help="Number of spaces to use for indentation in the output JSON",
            show_default=True,
        ),
    ] = 2,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Whether to overwrite the output file if it already exists",
            show_default=True,
        ),
    ] = False,
):
    """Fetches market orders for a given region ID from the EVE Online API and saves them to a file or prints them to stdout."""
    ######################
    # Create an EsiRequest
    ######################
    esi_request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsRegionIdOrders",
        path_parameters={"region_id": region_id},
        query_parameters={"order_type": "all"},
    )
    _process_request(
        esi_request=esi_request,
        output_directory=output_directory,
        filename=filename,
        indent=indent,
        overwrite=overwrite,
    )


#############################################################################
# These functions should be edited to be appropriate for the specific script.
#############################################################################


def _check_failed_response(
    esi_response: EsiResponse | FailedEsiResponse,
) -> EsiResponse:
    if isinstance(esi_response, FailedEsiResponse):
        typer.echo(
            f"Failed to fetch market orders for region "
            f"{esi_response.esi_request.path_parameters['region_id']}: "
            f"{esi_response.failed_response.error_messages}"
        )
        raise typer.Exit(code=1)
    return esi_response


def _generate_default_filename(esi_response: EsiResponse) -> str:
    """Generates a default filename for the market orders response based on the region ID and timestamp."""
    region_id = cast(int, esi_response.esi_request.path_parameters["region_id"])
    timestamp = esi_response.response.metadata.received_at.timestamp_nanos()
    return f"market_orders_{region_id}_{timestamp}.json"


def _process_response(esi_response: EsiResponse) -> MarketOrdersResponse:
    """Processes the ESI response and returns a structured MarketOrdersResponse."""
    orders_by_type: dict[int, DividedOrders] = {}
    region_id = cast(int, esi_response.esi_request.path_parameters["region_id"])

    for order in esi_response.response.json:
        type_id = order["type_id"]
        if type_id not in orders_by_type:
            orders_by_type[type_id] = {"buy_orders": [], "sell_orders": []}
        if order["is_buy_order"]:
            orders_by_type[type_id]["buy_orders"].append(order)
        else:
            orders_by_type[type_id]["sell_orders"].append(order)
    timestamp_iso = esi_response.response.metadata.received_at.format_iso()
    expires_at = (
        Instant.from_timestamp(esi_response.response.metadata.expires_at).format_iso()
        if esi_response.response.metadata.expires_at
        else None
    )
    return {
        "region_id": region_id,
        "timestamp_iso": timestamp_iso,
        "expires_at": expires_at,
        "orders": orders_by_type,
    }


################################################################
# These functions should not need to be edited for a new script.
################################################################
def _process_request(
    esi_request: EsiRequest,
    output_directory: Path,
    filename: str | None,
    indent: int,
    overwrite: bool,
) -> None:
    """Processes the ESI request and returns the response."""
    settings = get_settings()
    simple_requests = SimpleRequests(settings=settings)
    esi_schema = simple_requests.get_schema()
    response = asyncio.run(
        simple_requests.make_request(esi_request=esi_request, schema=esi_schema)
    )
    response = _check_failed_response(esi_response=response)
    processed_response = _process_response(esi_response=response)
    if output_directory != Path("-"):
        if filename is None:
            filename = _generate_default_filename(esi_response=response)
        try:
            output_path = save_text_file(
                text=json_io.json_dumps(processed_response, indent=indent),
                directory=output_directory,
                filename=filename,
                overwrite=overwrite,
            )
        except FileExistsError as e:
            typer.echo(
                f"File {output_directory / filename} already exists. Use --overwrite to overwrite it."
            )
            raise typer.Exit(code=1) from e
        typer.echo(
            f"Response expires at {response.expires_at_instant},  saved to {output_path}"
        )
        raise typer.Exit()
    print(json_io.json_dumps(processed_response, indent=indent))


if __name__ == "__main__":
    app()
