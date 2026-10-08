from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.output_port_access_types_get import OutputPortAccessTypesGet
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    include_output_port_count: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["include_output_port_count"] = include_output_port_count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/configuration/output_port_access_types",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | OutputPortAccessTypesGet | None:
    if response.status_code == 200:
        response_200 = OutputPortAccessTypesGet.from_dict(response.json())

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
) -> Response[HTTPValidationError | OutputPortAccessTypesGet]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_output_port_count: bool | Unset = False,
) -> Response[HTTPValidationError | OutputPortAccessTypesGet]:
    """Get Output Port Access Types

    Args:
        include_output_port_count (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OutputPortAccessTypesGet]
    """

    kwargs = _get_kwargs(
        include_output_port_count=include_output_port_count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    include_output_port_count: bool | Unset = False,
) -> HTTPValidationError | OutputPortAccessTypesGet | None:
    """Get Output Port Access Types

    Args:
        include_output_port_count (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OutputPortAccessTypesGet
    """

    return sync_detailed(
        client=client,
        include_output_port_count=include_output_port_count,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    include_output_port_count: bool | Unset = False,
) -> Response[HTTPValidationError | OutputPortAccessTypesGet]:
    """Get Output Port Access Types

    Args:
        include_output_port_count (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OutputPortAccessTypesGet]
    """

    kwargs = _get_kwargs(
        include_output_port_count=include_output_port_count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    include_output_port_count: bool | Unset = False,
) -> HTTPValidationError | OutputPortAccessTypesGet | None:
    """Get Output Port Access Types

    Args:
        include_output_port_count (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OutputPortAccessTypesGet
    """

    return (
        await asyncio_detailed(
            client=client,
            include_output_port_count=include_output_port_count,
        )
    ).parsed
