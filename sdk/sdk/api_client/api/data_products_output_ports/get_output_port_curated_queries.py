from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.output_port_curated_queries import OutputPortCuratedQueries
from ...types import Response


def _get_kwargs(
    data_product_id: UUID,
    id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/data_products/{data_product_id}/output_ports/{id}/curated_queries".format(
            data_product_id=quote(str(data_product_id), safe=""),
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | OutputPortCuratedQueries | None:
    if response.status_code == 200:
        response_200 = OutputPortCuratedQueries.from_dict(response.json())

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
) -> Response[HTTPValidationError | OutputPortCuratedQueries]:
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
) -> Response[HTTPValidationError | OutputPortCuratedQueries]:
    """Get Output Port Curated Queries

    Args:
        data_product_id (UUID):
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OutputPortCuratedQueries]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
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
) -> HTTPValidationError | OutputPortCuratedQueries | None:
    """Get Output Port Curated Queries

    Args:
        data_product_id (UUID):
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OutputPortCuratedQueries
    """

    return sync_detailed(
        data_product_id=data_product_id,
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | OutputPortCuratedQueries]:
    """Get Output Port Curated Queries

    Args:
        data_product_id (UUID):
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OutputPortCuratedQueries]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | OutputPortCuratedQueries | None:
    """Get Output Port Curated Queries

    Args:
        data_product_id (UUID):
        id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OutputPortCuratedQueries
    """

    return (
        await asyncio_detailed(
            data_product_id=data_product_id,
            id=id,
            client=client,
        )
    ).parsed
