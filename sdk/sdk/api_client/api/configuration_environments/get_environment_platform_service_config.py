from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.environment_configs_get_item import EnvironmentConfigsGetItem
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    id: UUID,
    platform_id: UUID,
    service_id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/configuration/environments/{id}/platforms/{platform_id}/services/{service_id}/config".format(
            id=quote(str(id), safe=""),
            platform_id=quote(str(platform_id), safe=""),
            service_id=quote(str(service_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> EnvironmentConfigsGetItem | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = EnvironmentConfigsGetItem.from_dict(response.json())

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
) -> Response[EnvironmentConfigsGetItem | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    platform_id: UUID,
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[EnvironmentConfigsGetItem | HTTPValidationError]:
    """Get Environment Platform Service Config

    Args:
        id (UUID):
        platform_id (UUID):
        service_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EnvironmentConfigsGetItem | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        id=id,
        platform_id=platform_id,
        service_id=service_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    platform_id: UUID,
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> EnvironmentConfigsGetItem | HTTPValidationError | None:
    """Get Environment Platform Service Config

    Args:
        id (UUID):
        platform_id (UUID):
        service_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EnvironmentConfigsGetItem | HTTPValidationError
    """

    return sync_detailed(
        id=id,
        platform_id=platform_id,
        service_id=service_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    platform_id: UUID,
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[EnvironmentConfigsGetItem | HTTPValidationError]:
    """Get Environment Platform Service Config

    Args:
        id (UUID):
        platform_id (UUID):
        service_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[EnvironmentConfigsGetItem | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        id=id,
        platform_id=platform_id,
        service_id=service_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    platform_id: UUID,
    service_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> EnvironmentConfigsGetItem | HTTPValidationError | None:
    """Get Environment Platform Service Config

    Args:
        id (UUID):
        platform_id (UUID):
        service_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        EnvironmentConfigsGetItem | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            id=id,
            platform_id=platform_id,
            service_id=service_id,
            client=client,
        )
    ).parsed
