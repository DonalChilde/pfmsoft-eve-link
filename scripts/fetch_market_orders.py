# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pfmsoft-eve-link>=0.4.5",
#     "typer>=0.26.8",
# ]
# [tool.uv]
# exclude-newer-package = {pfmsoft-eve-link = false}
# ///

####################################################################################################
# run with `uv run <script>`
# Add this to the script config header to use the dev branch of pfmsoft-eve-link:
# [tool.uv.sources]
# pfmsoft-eve-link = { git = "https://github.com/DonalChilde/pfmsoft-eve-link.git", branch = "dev" }
# And this to override a default dependency cool-down
# [tool.uv]
# exclude-newer-package = {pfmsoft-eve-link = false}
####################################################################################################

"""This script fetches market orders for a given region ID from the EVE Online API and saves them to a file or prints them to stdout."""

import asyncio
import logging
from pathlib import Path
from typing import Annotated, TypedDict, cast
from uuid import uuid4

import typer
from pfmsoft.eve_snippets import json_io, save_text_file
from rich.console import Console
from whenever import Instant

from pfmsoft.eve_link import EsiRequest, SimpleRequests
from pfmsoft.eve_link.esi_request.models import EsiResponse, FailedEsiResponse
from pfmsoft.eve_link.settings import get_settings

logger = logging.getLogger(__name__)
LOG_LEVEL = logging.WARNING

app = typer.Typer(no_args_is_help=True)


class DividedOrders(TypedDict):
    buy_orders: list[GetMarketsRegionIdOrdersDetail]
    sell_orders: list[GetMarketsRegionIdOrdersDetail]


class GetMarketsRegionIdOrdersDetail(TypedDict):
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
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            help="Whether to suppress status output messages",
            show_default=True,
        ),
    ] = False,
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Whether to overwrite the output file if it already exists",
            show_default=True,
        ),
    ] = False,
):
    """Fetches market orders for a given region ID from the EVE Online API.

    Response is saved to a file or printed to stdout.
    """
    if quiet:
        messenger = Console(stderr=True, quiet=True)
    else:
        messenger = Console(stderr=True)

    ######################
    # Create an EsiRequest
    ######################
    esi_request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsRegionIdOrders",
        path_parameters={"region_id": region_id},
        query_parameters={"order_type": "all"},
    )

    ###################################
    # Fetch the response and process it
    ###################################
    settings = get_settings()
    simple_requests = SimpleRequests(settings=settings)
    esi_schema = simple_requests.get_schema()
    response = asyncio.run(
        simple_requests.make_request(esi_request=esi_request, schema=esi_schema)
    )
    response = _check_failed_response(esi_response=response)
    processed_response = _process_response(esi_response=response)

    #######################################
    # Output the result to a file or stdout
    #######################################
    _output_result(
        response=response,
        data=processed_response,
        output_directory=output_directory,
        filename=filename,
        indent=indent,
        overwrite=overwrite,
        messenger=messenger,
    )


#############################################################################
# These functions should be edited to be appropriate for the specific script.
#############################################################################


def _generate_default_filename(esi_response: EsiResponse) -> str:
    """Generates a default filename for the market orders response based on the region ID and timestamp."""
    region_id = cast(int, esi_response.esi_request.path_parameters["region_id"])
    timestamp = esi_response.response.metadata.received_at.timestamp_nanos()
    return f"GetMarketsRegionIdOrders_{region_id}_{timestamp}.json"


def _process_response(esi_response: EsiResponse) -> MarketOrdersResponse:
    """Processes the ESI response and returns a structured MarketOrdersResponse."""
    if not isinstance(esi_response.response_data, list):
        raise ValueError(
            f"Expected a list of market orders, but got: {type(esi_response.response_data)}"
        )
    orders_by_type: dict[int, DividedOrders] = {}
    region_id = cast(int, esi_response.esi_request.path_parameters["region_id"])
    data = cast(list[GetMarketsRegionIdOrdersDetail], esi_response.response_data)  # type: ignore
    for order in data:
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
def _check_failed_response(
    esi_response: EsiResponse | FailedEsiResponse,
) -> EsiResponse:
    """Checks if the ESI response is a failed response and raises an error if so."""
    if isinstance(esi_response, FailedEsiResponse):
        logger.error("Failed response: %r", esi_response)
        raise ValueError(
            f"Failed request to: {esi_response.esi_request.operation_id}, "
            f"error messages: {esi_response.failed_response.error_messages}"
        )
    return esi_response


def _output_result(
    response: EsiResponse,
    data: MarketOrdersResponse,
    output_directory: Path,
    filename: str | None,
    indent: int,
    overwrite: bool,
    messenger: Console,
) -> None:
    """Outputs the data to a file or stdout."""
    if output_directory != Path("-"):
        if filename is None:
            filename = _generate_default_filename(esi_response=response)
        try:
            output_path = save_text_file(
                text=json_io.json_dumps(data, indent=indent),
                directory=output_directory,
                filename=filename,
                overwrite=overwrite,
            )
        except FileExistsError as e:
            messenger.print(
                f"File {output_directory / filename} already exists. Use --overwrite to overwrite it."
            )
            raise typer.Exit(code=1) from e
        messenger.print(
            f"Response from {response.esi_request.operation_id} expires at "
            f"{response.expires_at_instant}, saved to {output_path}"
        )
        raise typer.Exit()
    print(json_io.json_dumps(data, indent=indent))


if __name__ == "__main__":
    logging.basicConfig(level=LOG_LEVEL)
    app()
