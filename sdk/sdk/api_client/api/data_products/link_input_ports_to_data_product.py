from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.link_input_ports_to_data_product import LinkInputPortsToDataProduct
from ...models.link_input_ports_to_data_product_post import (
    LinkInputPortsToDataProductPost,
)
from ...types import Response


def _get_kwargs(
    id: UUID,
    *,
    body: LinkInputPortsToDataProduct,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/data_products/{id}/link_input_ports".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | LinkInputPortsToDataProductPost | None:
    if response.status_code == 200:
        response_200 = LinkInputPortsToDataProductPost.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError | LinkInputPortsToDataProductPost]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: LinkInputPortsToDataProduct,
) -> Response[Any | HTTPValidationError | LinkInputPortsToDataProductPost]:
    """Link Input Ports To Data Product

    Args:
        id (UUID):
        body (LinkInputPortsToDataProduct):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | LinkInputPortsToDataProductPost]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: LinkInputPortsToDataProduct,
) -> Any | HTTPValidationError | LinkInputPortsToDataProductPost | None:
    """Link Input Ports To Data Product

    Args:
        id (UUID):
        body (LinkInputPortsToDataProduct):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | LinkInputPortsToDataProductPost
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: LinkInputPortsToDataProduct,
) -> Response[Any | HTTPValidationError | LinkInputPortsToDataProductPost]:
    """Link Input Ports To Data Product

    Args:
        id (UUID):
        body (LinkInputPortsToDataProduct):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | LinkInputPortsToDataProductPost]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: LinkInputPortsToDataProduct,
) -> Any | HTTPValidationError | LinkInputPortsToDataProductPost | None:
    """Link Input Ports To Data Product

    Args:
        id (UUID):
        body (LinkInputPortsToDataProduct):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | LinkInputPortsToDataProductPost
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
