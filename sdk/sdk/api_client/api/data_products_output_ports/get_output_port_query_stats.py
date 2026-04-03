from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.output_port_query_stats_responses import OutputPortQueryStatsResponses
from ...models.query_stats_granularity import QueryStatsGranularity
from ...types import UNSET, Response, Unset


def _get_kwargs(
    data_product_id: UUID,
    id: UUID,
    *,
    granularity: QueryStatsGranularity | Unset = UNSET,
    day_range: int | Unset = 90,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_granularity: str | Unset = UNSET
    if not isinstance(granularity, Unset):
        json_granularity = granularity.value

    params["granularity"] = json_granularity

    params["day_range"] = day_range

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/data_products/{data_product_id}/output_ports/{id}/query_stats".format(
            data_product_id=quote(str(data_product_id), safe=""),
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | OutputPortQueryStatsResponses | None:
    if response.status_code == 200:
        response_200 = OutputPortQueryStatsResponses.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | OutputPortQueryStatsResponses]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    granularity: QueryStatsGranularity | Unset = UNSET,
    day_range: int | Unset = 90,
) -> Response[HTTPValidationError | OutputPortQueryStatsResponses]:
    """Get Output Port Query Stats

    Args:
        data_product_id (UUID):
        id (UUID):
        granularity (QueryStatsGranularity | Unset):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OutputPortQueryStatsResponses]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        granularity=granularity,
        day_range=day_range,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    granularity: QueryStatsGranularity | Unset = UNSET,
    day_range: int | Unset = 90,
) -> HTTPValidationError | OutputPortQueryStatsResponses | None:
    """Get Output Port Query Stats

    Args:
        data_product_id (UUID):
        id (UUID):
        granularity (QueryStatsGranularity | Unset):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OutputPortQueryStatsResponses
    """

    return sync_detailed(
        data_product_id=data_product_id,
        id=id,
        client=client,
        granularity=granularity,
        day_range=day_range,
    ).parsed


async def asyncio_detailed(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    granularity: QueryStatsGranularity | Unset = UNSET,
    day_range: int | Unset = 90,
) -> Response[HTTPValidationError | OutputPortQueryStatsResponses]:
    """Get Output Port Query Stats

    Args:
        data_product_id (UUID):
        id (UUID):
        granularity (QueryStatsGranularity | Unset):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OutputPortQueryStatsResponses]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        granularity=granularity,
        day_range=day_range,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    granularity: QueryStatsGranularity | Unset = UNSET,
    day_range: int | Unset = 90,
) -> HTTPValidationError | OutputPortQueryStatsResponses | None:
    """Get Output Port Query Stats

    Args:
        data_product_id (UUID):
        id (UUID):
        granularity (QueryStatsGranularity | Unset):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OutputPortQueryStatsResponses
    """

    return (
        await asyncio_detailed(
            data_product_id=data_product_id,
            id=id,
            client=client,
            granularity=granularity,
            day_range=day_range,
        )
    ).parsed
