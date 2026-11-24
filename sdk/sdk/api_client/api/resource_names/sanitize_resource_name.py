from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.resource_name_suggestion import ResourceNameSuggestion
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    name: str,
    technical_asset_type: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["name"] = name

    json_technical_asset_type: None | str | Unset
    if isinstance(technical_asset_type, Unset):
        json_technical_asset_type = UNSET
    else:
        json_technical_asset_type = technical_asset_type
    params["technical_asset_type"] = json_technical_asset_type

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/resource_names/sanitize",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ResourceNameSuggestion | None:
    if response.status_code == 200:
        response_200 = ResourceNameSuggestion.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResourceNameSuggestion]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str,
    technical_asset_type: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResourceNameSuggestion]:
    """Sanitize Resource Name

    Args:
        name (str):
        technical_asset_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResourceNameSuggestion]
    """

    kwargs = _get_kwargs(
        name=name,
        technical_asset_type=technical_asset_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    name: str,
    technical_asset_type: None | str | Unset = UNSET,
) -> HTTPValidationError | ResourceNameSuggestion | None:
    """Sanitize Resource Name

    Args:
        name (str):
        technical_asset_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResourceNameSuggestion
    """

    return sync_detailed(
        client=client,
        name=name,
        technical_asset_type=technical_asset_type,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    name: str,
    technical_asset_type: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | ResourceNameSuggestion]:
    """Sanitize Resource Name

    Args:
        name (str):
        technical_asset_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResourceNameSuggestion]
    """

    kwargs = _get_kwargs(
        name=name,
        technical_asset_type=technical_asset_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    name: str,
    technical_asset_type: None | str | Unset = UNSET,
) -> HTTPValidationError | ResourceNameSuggestion | None:
    """Sanitize Resource Name

    Args:
        name (str):
        technical_asset_type (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResourceNameSuggestion
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            technical_asset_type=technical_asset_type,
        )
    ).parsed
