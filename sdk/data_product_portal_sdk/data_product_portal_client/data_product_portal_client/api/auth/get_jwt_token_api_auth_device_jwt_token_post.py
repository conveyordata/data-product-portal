from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    client_id: str,
    device_code: str,
    grant_type: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["client_id"] = client_id

    params["device_code"] = device_code

    params["grant_type"] = grant_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/auth/device/jwt_token",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Union[Any, HTTPValidationError]]:
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
    device_code: str,
    grant_type: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Get Jwt Token

    Args:
        client_id (str):
        device_code (str):
        grant_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        device_code=device_code,
        grant_type=grant_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    client_id: str,
    device_code: str,
    grant_type: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Get Jwt Token

    Args:
        client_id (str):
        device_code (str):
        grant_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        client_id=client_id,
        device_code=device_code,
        grant_type=grant_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    client_id: str,
    device_code: str,
    grant_type: str,
) -> Response[Union[Any, HTTPValidationError]]:
    """Get Jwt Token

    Args:
        client_id (str):
        device_code (str):
        grant_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        client_id=client_id,
        device_code=device_code,
        grant_type=grant_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    client_id: str,
    device_code: str,
    grant_type: str,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Get Jwt Token

    Args:
        client_id (str):
        device_code (str):
        grant_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            client_id=client_id,
            device_code=device_code,
            grant_type=grant_type,
        )
    ).parsed
