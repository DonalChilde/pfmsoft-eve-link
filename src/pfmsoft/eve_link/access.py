"""Convenience functions for accessing EVE Online API endpoints.

Functions are named after the ESI operation ID, which results in non-standard Python
function names. This is intentional to make it easier to find the function corresponding
to a specific ESI operation.

Functions may also have an alternate signature to support easier access. For example,
the GetMarketsGroupsMarketGroupId end point takes a single market_group_id as a path
parameter, but the function GetMarketsGroupsMarketGroupId takes a list of market_group_ids
and returns a EsiResponseGroup containing the responses for each market group.
"""
# TODO add support for response language, as appropriate.
# TODO consider a better module name than access.py.

from uuid import uuid4

from pfmsoft.eve_link import (
    EsiLink,
    EsiRequest,
    EsiRequestGroup,
    EsiResponse,
    EsiResponseGroup,
    EsiSchema,
    FailedEsiResponse,
)


async def GetMarketsGroups(
    esi_link: EsiLink, esi_schema: EsiSchema
) -> EsiResponse | FailedEsiResponse:
    """Fetches the list of market group IDs from the EVE Online API."""
    market_groups_request = EsiRequest(
        request_id=uuid4(),
        operation_id="GetMarketsGroups",
    )
    return await esi_link.make_request(
        esi_request=market_groups_request, schema=esi_schema
    )


async def GetMarketsGroupsMarketGroupId(
    esi_link: EsiLink, esi_schema: EsiSchema, *, market_group_ids: list[int]
) -> EsiResponseGroup:
    """Fetches the details for each market group ID from the EVE Online API."""
    requests = [
        EsiRequest(
            request_id=uuid4(),
            operation_id="GetMarketsGroupsMarketGroupId",
            path_parameters={"market_group_id": market_group_id},
        )
        for market_group_id in market_group_ids
    ]
    request_group = EsiRequestGroup(requests={r.request_id: r for r in requests})
    return await esi_link.make_requests(esi_requests=request_group, schema=esi_schema)
