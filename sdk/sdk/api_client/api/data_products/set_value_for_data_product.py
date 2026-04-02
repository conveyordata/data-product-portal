from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    id: UUID,
    setting_id: UUID,
    *,
    value: str,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["value"] = value

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/data_products/{id}/settings/{setting_id}".format(
            id=quote(str(id), safe=""),
            setting_id=quote(str(setting_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | None:
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
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    setting_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    value: str,
) -> Response[Any | HTTPValidationError]:
    """Set Value For Data Product

    Args:
        id (UUID):
        setting_id (UUID):
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        id=id,
        setting_id=setting_id,
        value=value,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    setting_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    value: str,
) -> Any | HTTPValidationError | None:
    """Set Value For Data Product

    Args:
        id (UUID):
        setting_id (UUID):
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return sync_detailed(
        id=id,
        setting_id=setting_id,
        client=client,
        value=value,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    setting_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    value: str,
) -> Response[Any | HTTPValidationError]:
    """Set Value For Data Product

    Args:
        id (UUID):
        setting_id (UUID):
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        id=id,
        setting_id=setting_id,
        value=value,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    setting_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    value: str,
) -> Any | HTTPValidationError | None:
    """Set Value For Data Product

    Args:
        id (UUID):
        setting_id (UUID):
        value (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            id=id,
            setting_id=setting_id,
            client=client,
            value=value,
        )
    ).parsed
