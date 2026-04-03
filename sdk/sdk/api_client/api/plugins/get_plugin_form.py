from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.ui_element_metadata_response import UIElementMetadataResponse
from ...types import Response


def _get_kwargs(
    plugin_name: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/plugins/{plugin_name}/form".format(
            plugin_name=quote(str(plugin_name), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | UIElementMetadataResponse | None:
    if response.status_code == 200:
        response_200 = UIElementMetadataResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | UIElementMetadataResponse]:
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
) -> Response[HTTPValidationError | UIElementMetadataResponse]:
    """Get Plugin Form

     Get form metadata for a specific plugin (ADR-compliant endpoint)

    Args:
        plugin_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UIElementMetadataResponse]
    """

    kwargs = _get_kwargs(
        plugin_name=plugin_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    plugin_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | UIElementMetadataResponse | None:
    """Get Plugin Form

     Get form metadata for a specific plugin (ADR-compliant endpoint)

    Args:
        plugin_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UIElementMetadataResponse
    """

    return sync_detailed(
        plugin_name=plugin_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    plugin_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | UIElementMetadataResponse]:
    """Get Plugin Form

     Get form metadata for a specific plugin (ADR-compliant endpoint)

    Args:
        plugin_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | UIElementMetadataResponse]
    """

    kwargs = _get_kwargs(
        plugin_name=plugin_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    plugin_name: str,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | UIElementMetadataResponse | None:
    """Get Plugin Form

     Get form metadata for a specific plugin (ADR-compliant endpoint)

    Args:
        plugin_name (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | UIElementMetadataResponse
    """

    return (
        await asyncio_detailed(
            plugin_name=plugin_name,
            client=client,
        )
    ).parsed
