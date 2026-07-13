from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.my_requests_response import MyRequestsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    hide_old_inactive: bool | Unset = True,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["hide_old_inactive"] = hide_old_inactive

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/users/current/my_requests",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | MyRequestsResponse | None:
    if response.status_code == 200:
        response_200 = MyRequestsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | MyRequestsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    hide_old_inactive: bool | Unset = True,
) -> Response[HTTPValidationError | MyRequestsResponse]:
    """Get User Requests

    Args:
        hide_old_inactive (bool | Unset): Filter out inactive requests older than 30 days Default:
            True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MyRequestsResponse]
    """

    kwargs = _get_kwargs(
        hide_old_inactive=hide_old_inactive,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    hide_old_inactive: bool | Unset = True,
) -> HTTPValidationError | MyRequestsResponse | None:
    """Get User Requests

    Args:
        hide_old_inactive (bool | Unset): Filter out inactive requests older than 30 days Default:
            True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MyRequestsResponse
    """

    return sync_detailed(
        client=client,
        hide_old_inactive=hide_old_inactive,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    hide_old_inactive: bool | Unset = True,
) -> Response[HTTPValidationError | MyRequestsResponse]:
    """Get User Requests

    Args:
        hide_old_inactive (bool | Unset): Filter out inactive requests older than 30 days Default:
            True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | MyRequestsResponse]
    """

    kwargs = _get_kwargs(
        hide_old_inactive=hide_old_inactive,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    hide_old_inactive: bool | Unset = True,
) -> HTTPValidationError | MyRequestsResponse | None:
    """Get User Requests

    Args:
        hide_old_inactive (bool | Unset): Filter out inactive requests older than 30 days Default:
            True.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | MyRequestsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            hide_old_inactive=hide_old_inactive,
        )
    ).parsed
