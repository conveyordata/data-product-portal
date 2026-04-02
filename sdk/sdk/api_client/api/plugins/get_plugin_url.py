from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.url_response import URLResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    plugin_name: str,
    *,
    id: UUID,
    environment: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_id = str(id)
    params["id"] = json_id

    json_environment: None | str | Unset
    if isinstance(environment, Unset):
        json_environment = UNSET
    else:
        json_environment = environment
    params["environment"] = json_environment

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/plugins/{plugin_name}/url".format(
            plugin_name=quote(str(plugin_name), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | URLResponse | None:
    if response.status_code == 200:
        response_200 = URLResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | URLResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    plugin_name: str,
    *,
    client: AuthenticatedClient | Client,
    id: UUID,
    environment: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | URLResponse]:
    """Get Plugin Url

     Get the URL for the access tile of a specific plugin

    Args:
        plugin_name (str):
        id (UUID):
        environment (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | URLResponse]
    """

    kwargs = _get_kwargs(
        plugin_name=plugin_name,
        id=id,
        environment=environment,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    plugin_name: str,
    *,
    client: AuthenticatedClient | Client,
    id: UUID,
    environment: None | str | Unset = UNSET,
) -> HTTPValidationError | URLResponse | None:
    """Get Plugin Url

     Get the URL for the access tile of a specific plugin

    Args:
        plugin_name (str):
        id (UUID):
        environment (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | URLResponse
    """

    return sync_detailed(
        plugin_name=plugin_name,
        client=client,
        id=id,
        environment=environment,
    ).parsed


async def asyncio_detailed(
    plugin_name: str,
    *,
    client: AuthenticatedClient | Client,
    id: UUID,
    environment: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | URLResponse]:
    """Get Plugin Url

     Get the URL for the access tile of a specific plugin

    Args:
        plugin_name (str):
        id (UUID):
        environment (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | URLResponse]
    """

    kwargs = _get_kwargs(
        plugin_name=plugin_name,
        id=id,
        environment=environment,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    plugin_name: str,
    *,
    client: AuthenticatedClient | Client,
    id: UUID,
    environment: None | str | Unset = UNSET,
) -> HTTPValidationError | URLResponse | None:
    """Get Plugin Url

     Get the URL for the access tile of a specific plugin

    Args:
        plugin_name (str):
        id (UUID):
        environment (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | URLResponse
    """

    return (
        await asyncio_detailed(
            plugin_name=plugin_name,
            client=client,
            id=id,
            environment=environment,
        )
    ).parsed
