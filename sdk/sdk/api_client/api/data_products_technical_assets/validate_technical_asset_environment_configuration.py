from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.technical_asset_environment_configuration_update import (
    TechnicalAssetEnvironmentConfigurationUpdate,
)
from ...types import Response


def _get_kwargs(
    data_product_id: UUID,
    id: UUID,
    *,
    body: TechnicalAssetEnvironmentConfigurationUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/data_products/{data_product_id}/technical_assets/{id}/environment_configuration/validate".format(
            data_product_id=quote(str(data_product_id), safe=""),
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | None:
    if response.status_code == 200:
        return None

    if response.status_code == 404:
        return None

    if response.status_code == 422:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: TechnicalAssetEnvironmentConfigurationUpdate,
) -> Response[Any]:
    """Validate Technical Asset Environment Configuration

    Args:
        data_product_id (UUID):
        id (UUID):
        body (TechnicalAssetEnvironmentConfigurationUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    data_product_id: UUID,
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: TechnicalAssetEnvironmentConfigurationUpdate,
) -> Response[Any]:
    """Validate Technical Asset Environment Configuration

    Args:
        data_product_id (UUID):
        id (UUID):
        body (TechnicalAssetEnvironmentConfigurationUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
