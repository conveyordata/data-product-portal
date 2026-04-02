from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.graph import Graph
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    data_product_id: UUID,
    id: UUID,
    *,
    level: int | Unset = 3,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["level"] = level

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/data_products/{data_product_id}/technical_assets/{id}/graph".format(
            data_product_id=quote(str(data_product_id), safe=""),
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Graph | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = Graph.from_dict(response.json())

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
) -> Response[Graph | HTTPValidationError]:
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
    level: int | Unset = 3,
) -> Response[Graph | HTTPValidationError]:
    """Get Technical Asset Graph Data

    Args:
        data_product_id (UUID):
        id (UUID):
        level (int | Unset):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Graph | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        level=level,
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
    level: int | Unset = 3,
) -> Graph | HTTPValidationError | None:
    """Get Technical Asset Graph Data

    Args:
        data_product_id (UUID):
        id (UUID):
        level (int | Unset):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Graph | HTTPValidationError
    """

    return sync_detailed(
        data_product_id=data_product_id,
        id=id,
        client=client,
        level=level,
    ).parsed


async def asyncio_detailed(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    level: int | Unset = 3,
) -> Response[Graph | HTTPValidationError]:
    """Get Technical Asset Graph Data

    Args:
        data_product_id (UUID):
        id (UUID):
        level (int | Unset):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Graph | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        level=level,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    level: int | Unset = 3,
) -> Graph | HTTPValidationError | None:
    """Get Technical Asset Graph Data

    Args:
        data_product_id (UUID):
        id (UUID):
        level (int | Unset):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Graph | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            data_product_id=data_product_id,
            id=id,
            client=client,
            level=level,
        )
    ).parsed
