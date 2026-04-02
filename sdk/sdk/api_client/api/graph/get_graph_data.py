from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.graph import Graph
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    data_product_nodes_enabled: bool | Unset = True,
    output_port_nodes_enabled: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["data_product_nodes_enabled"] = data_product_nodes_enabled

    params["output_port_nodes_enabled"] = output_port_nodes_enabled

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/graph",
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
    *,
    client: AuthenticatedClient | Client,
    data_product_nodes_enabled: bool | Unset = True,
    output_port_nodes_enabled: bool | Unset = True,
) -> Response[Graph | HTTPValidationError]:
    """Get Graph Data

    Args:
        data_product_nodes_enabled (bool | Unset):  Default: True.
        output_port_nodes_enabled (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Graph | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_nodes_enabled=data_product_nodes_enabled,
        output_port_nodes_enabled=output_port_nodes_enabled,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    data_product_nodes_enabled: bool | Unset = True,
    output_port_nodes_enabled: bool | Unset = True,
) -> Graph | HTTPValidationError | None:
    """Get Graph Data

    Args:
        data_product_nodes_enabled (bool | Unset):  Default: True.
        output_port_nodes_enabled (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Graph | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        data_product_nodes_enabled=data_product_nodes_enabled,
        output_port_nodes_enabled=output_port_nodes_enabled,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    data_product_nodes_enabled: bool | Unset = True,
    output_port_nodes_enabled: bool | Unset = True,
) -> Response[Graph | HTTPValidationError]:
    """Get Graph Data

    Args:
        data_product_nodes_enabled (bool | Unset):  Default: True.
        output_port_nodes_enabled (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Graph | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_nodes_enabled=data_product_nodes_enabled,
        output_port_nodes_enabled=output_port_nodes_enabled,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    data_product_nodes_enabled: bool | Unset = True,
    output_port_nodes_enabled: bool | Unset = True,
) -> Graph | HTTPValidationError | None:
    """Get Graph Data

    Args:
        data_product_nodes_enabled (bool | Unset):  Default: True.
        output_port_nodes_enabled (bool | Unset):  Default: True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Graph | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            data_product_nodes_enabled=data_product_nodes_enabled,
            output_port_nodes_enabled=output_port_nodes_enabled,
        )
    ).parsed
