from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.oidc_token_response import OIDCTokenResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    device_code: str,
    grant_type: str,
    client_id: str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["device_code"] = device_code

    params["grant_type"] = grant_type

    params["client_id"] = client_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/authn/device/jwt_token",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | OIDCTokenResponse | None:
    if response.status_code == 200:
        response_200 = OIDCTokenResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | OIDCTokenResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    device_code: str,
    grant_type: str,
    client_id: str | Unset = UNSET,
) -> Response[HTTPValidationError | OIDCTokenResponse]:
    """Get Jwt Token

    Args:
        device_code (str):
        grant_type (str):
        client_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OIDCTokenResponse]
    """

    kwargs = _get_kwargs(
        device_code=device_code,
        grant_type=grant_type,
        client_id=client_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    device_code: str,
    grant_type: str,
    client_id: str | Unset = UNSET,
) -> HTTPValidationError | OIDCTokenResponse | None:
    """Get Jwt Token

    Args:
        device_code (str):
        grant_type (str):
        client_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OIDCTokenResponse
    """

    return sync_detailed(
        client=client,
        device_code=device_code,
        grant_type=grant_type,
        client_id=client_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    device_code: str,
    grant_type: str,
    client_id: str | Unset = UNSET,
) -> Response[HTTPValidationError | OIDCTokenResponse]:
    """Get Jwt Token

    Args:
        device_code (str):
        grant_type (str):
        client_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | OIDCTokenResponse]
    """

    kwargs = _get_kwargs(
        device_code=device_code,
        grant_type=grant_type,
        client_id=client_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    device_code: str,
    grant_type: str,
    client_id: str | Unset = UNSET,
) -> HTTPValidationError | OIDCTokenResponse | None:
    """Get Jwt Token

    Args:
        device_code (str):
        grant_type (str):
        client_id (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | OIDCTokenResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            device_code=device_code,
            grant_type=grant_type,
            client_id=client_id,
        )
    ).parsed
