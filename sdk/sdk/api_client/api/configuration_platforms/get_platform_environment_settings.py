from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.platform_environment_settings import PlatformEnvironmentSettings
from ...types import Response


def _get_kwargs(
    platform_key: str,
    environment_id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/configuration/platforms/{platform_key}/environments/{environment_id}/settings".format(
            platform_key=quote(str(platform_key), safe=""),
            environment_id=quote(str(environment_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PlatformEnvironmentSettings | None:
    if response.status_code == 200:
        response_200 = PlatformEnvironmentSettings.from_dict(response.json())

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
) -> Response[HTTPValidationError | PlatformEnvironmentSettings]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    platform_key: str,
    environment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | PlatformEnvironmentSettings]:
    """Get Platform Environment Settings

    Args:
        platform_key (str):
        environment_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PlatformEnvironmentSettings]
    """

    kwargs = _get_kwargs(
        platform_key=platform_key,
        environment_id=environment_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    platform_key: str,
    environment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | PlatformEnvironmentSettings | None:
    """Get Platform Environment Settings

    Args:
        platform_key (str):
        environment_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PlatformEnvironmentSettings
    """

    return sync_detailed(
        platform_key=platform_key,
        environment_id=environment_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    platform_key: str,
    environment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | PlatformEnvironmentSettings]:
    """Get Platform Environment Settings

    Args:
        platform_key (str):
        environment_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PlatformEnvironmentSettings]
    """

    kwargs = _get_kwargs(
        platform_key=platform_key,
        environment_id=environment_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    platform_key: str,
    environment_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | PlatformEnvironmentSettings | None:
    """Get Platform Environment Settings

    Args:
        platform_key (str):
        environment_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PlatformEnvironmentSettings
    """

    return (
        await asyncio_detailed(
            platform_key=platform_key,
            environment_id=environment_id,
            client=client,
        )
    ).parsed
