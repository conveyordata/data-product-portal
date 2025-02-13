from http import HTTPStatus
from typing import Any, Optional, Union
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.graph import Graph
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: UUID,
    *,
    level: Union[Unset, int] = 3,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["level"] = level

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/data_products/{id}/graph",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Graph, HTTPValidationError]]:
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
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Graph, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient,
    level: Union[Unset, int] = 3,
) -> Response[Union[Graph, HTTPValidationError]]:
    """Get Graph Data

    Args:
        id (UUID):
        level (Union[Unset, int]):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Graph, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        id=id,
        level=level,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    *,
    client: AuthenticatedClient,
    level: Union[Unset, int] = 3,
) -> Optional[Union[Graph, HTTPValidationError]]:
    """Get Graph Data

    Args:
        id (UUID):
        level (Union[Unset, int]):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Graph, HTTPValidationError]
    """

    return sync_detailed(
        id=id,
        client=client,
        level=level,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient,
    level: Union[Unset, int] = 3,
) -> Response[Union[Graph, HTTPValidationError]]:
    """Get Graph Data

    Args:
        id (UUID):
        level (Union[Unset, int]):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Graph, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        id=id,
        level=level,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    *,
    client: AuthenticatedClient,
    level: Union[Unset, int] = 3,
) -> Optional[Union[Graph, HTTPValidationError]]:
    """Get Graph Data

    Args:
        id (UUID):
        level (Union[Unset, int]):  Default: 3.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Graph, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            level=level,
        )
    ).parsed
