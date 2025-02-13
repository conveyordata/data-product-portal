from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.device_flow import DeviceFlow
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client_id: str,
    scope: Union[Unset, str] = "openid",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["client_id"] = client_id

    params["scope"] = scope

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/auth/device/device_token",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DeviceFlow, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = DeviceFlow.from_dict(response.json())

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
) -> Response[Union[DeviceFlow, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    client_id: str,
    scope: Union[Unset, str] = "openid",
) -> Response[Union[DeviceFlow, HTTPValidationError]]:
    """Get Device Token

    Args:
        client_id (str):
        scope (Union[Unset, str]):  Default: 'openid'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceFlow, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        scope=scope,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    client_id: str,
    scope: Union[Unset, str] = "openid",
) -> Optional[Union[DeviceFlow, HTTPValidationError]]:
    """Get Device Token

    Args:
        client_id (str):
        scope (Union[Unset, str]):  Default: 'openid'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceFlow, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        client_id=client_id,
        scope=scope,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    client_id: str,
    scope: Union[Unset, str] = "openid",
) -> Response[Union[DeviceFlow, HTTPValidationError]]:
    """Get Device Token

    Args:
        client_id (str):
        scope (Union[Unset, str]):  Default: 'openid'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DeviceFlow, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        scope=scope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    client_id: str,
    scope: Union[Unset, str] = "openid",
) -> Optional[Union[DeviceFlow, HTTPValidationError]]:
    """Get Device Token

    Args:
        client_id (str):
        scope (Union[Unset, str]):  Default: 'openid'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DeviceFlow, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            client_id=client_id,
            scope=scope,
        )
    ).parsed
