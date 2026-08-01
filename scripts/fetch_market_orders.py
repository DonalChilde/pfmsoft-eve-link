# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "pfmsoft-eve-link>=0.4.1",
#     "typer>=0.26.8",
# ]
# ///

# run with `uv run <script>`

"""This script fetches market orders for a given region ID from the EVE Online API and saves them to a file or prints them to stdout."""

import asyncio
from pathlib import Path
from typing import Annotated, TypedDict, cast
from uuid import uuid4

import typer
from pfmsoft.eve_snippets import json_io, save_text_file
from pfmsoft.eve_snippets.httpx2.http_session_factory import client_manager

from pfmsoft.eve_link import EsiRequest, make_request
from pfmsoft.eve_link.esi_request.models import EsiResponse, FailedEsiResponse
from pfmsoft.eve_link.schema.cache.schema_cache_disk import SchemaCacheManager
from pfmsoft.eve_link.schema.models import EsiSchema
from pfmsoft.eve_link.settings import USER_AGENT, EsiLinkSettings, get_settings

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
    timestamp: int
    orders: OrdersDict


@app.command()
def main(
    region_id: Annotated[
        int,
        typer.Option("--region_id", help="The region ID to fetch market orders for"),
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
    esi_request: EsiRequest, esi_response: EsiResponse | FailedEsiResponse
) -> EsiResponse:
    if isinstance(esi_response, FailedEsiResponse):
        typer.echo(
            f"Failed to fetch market orders for region {esi_request.path_parameters['region_id']}: {esi_response.failed_response.error_messages}"
        )
        raise typer.Exit(code=1)
    return esi_response


def _generate_default_filename(
    esi_request: EsiRequest, esi_response: EsiResponse
) -> str:
    """Generates a default filename for the market orders response based on the region ID and timestamp."""
    region_id = cast(int, esi_request.path_parameters["region_id"])
    timestamp = esi_response.response.metadata.received_at.timestamp()
    return f"market_orders_{region_id}_{timestamp}.json"


def _process_response(
    esi_request: EsiRequest, esi_response: EsiResponse
) -> MarketOrdersResponse:
    """Processes the ESI response and returns a structured MarketOrdersResponse."""
    orders_by_type: dict[int, DividedOrders] = {}
    region_id = cast(int, esi_request.path_parameters["region_id"])

    for order in esi_response.response.json:
        type_id = order["type_id"]
        if type_id not in orders_by_type:
            orders_by_type[type_id] = {"buy_orders": [], "sell_orders": []}
        if order["is_buy_order"]:
            orders_by_type[type_id]["buy_orders"].append(order)
        else:
            orders_by_type[type_id]["sell_orders"].append(order)
    return {
        "region_id": region_id,
        "timestamp": esi_response.response.metadata.received_at.timestamp(),
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
    esi_schema = _get_schema(settings)
    response = asyncio.run(
        make_request(request=esi_request, settings=settings, schema=esi_schema)
    )
    response = _check_failed_response(esi_request=esi_request, esi_response=response)
    processed_response = _process_response(
        esi_request=esi_request, esi_response=response
    )
    if output_directory != Path("-"):
        if filename is None:
            filename = _generate_default_filename(
                esi_request=esi_request, esi_response=response
            )
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
        # TODO add cache expires in ? seconds.
        typer.echo(f"Response saved to {output_path}")
        raise typer.Exit()
    print(json_io.json_dumps(processed_response, indent=indent))


def _get_schema(settings: EsiLinkSettings) -> EsiSchema:
    """Fetches the latest ESI schema from the EsiLink schema cache."""
    schema_manager = SchemaCacheManager(cache_directory=settings.schema_cache_directory)
    with client_manager(USER_AGENT) as session:
        schema_manager.fetch_updates(session=session)
    esi_schema = schema_manager.latest_schema()
    if esi_schema is None:
        typer.echo(
            f"Failed to fetch the latest schema. Please update your schema cache and try again."
        )
        raise typer.Exit(code=1)
    return esi_schema


if __name__ == "__main__":
    app()
