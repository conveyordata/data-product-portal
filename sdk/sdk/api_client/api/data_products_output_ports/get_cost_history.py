from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cost_history_response import CostHistoryResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    data_product_id: UUID,
    id: UUID,
    *,
    day_range: int | Unset = 90,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["day_range"] = day_range

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/data_products/{data_product_id}/output_ports/{id}/cost".format(
            data_product_id=quote(str(data_product_id), safe=""),
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CostHistoryResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CostHistoryResponse.from_dict(response.json())

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
) -> Response[CostHistoryResponse | HTTPValidationError]:
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
    day_range: int | Unset = 90,
) -> Response[CostHistoryResponse | HTTPValidationError]:
    """Get Cost History

    Args:
        data_product_id (UUID):
        id (UUID):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CostHistoryResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
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
    day_range: int | Unset = 90,
) -> CostHistoryResponse | HTTPValidationError | None:
    """Get Cost History

    Args:
        data_product_id (UUID):
        id (UUID):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CostHistoryResponse | HTTPValidationError
    """

    return sync_detailed(
        data_product_id=data_product_id,
        id=id,
        client=client,
        day_range=day_range,
    ).parsed


async def asyncio_detailed(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    day_range: int | Unset = 90,
) -> Response[CostHistoryResponse | HTTPValidationError]:
    """Get Cost History

    Args:
        data_product_id (UUID):
        id (UUID):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CostHistoryResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        day_range=day_range,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    day_range: int | Unset = 90,
) -> CostHistoryResponse | HTTPValidationError | None:
    """Get Cost History

    Args:
        data_product_id (UUID):
        id (UUID):
        day_range (int | Unset):  Default: 90.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CostHistoryResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            data_product_id=data_product_id,
            id=id,
            client=client,
            day_range=day_range,
        )
    ).parsed
