from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_tool_request import CreateToolRequest
from ...models.create_tool_response import CreateToolResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    data_product_id: UUID,
    *,
    body: CreateToolRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/data_products/{data_product_id}/tools".format(
            data_product_id=quote(str(data_product_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CreateToolResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CreateToolResponse.from_dict(response.json())

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
) -> Response[CreateToolResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    data_product_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolRequest,
) -> Response[CreateToolResponse | HTTPValidationError]:
    """Create Tool

    Args:
        data_product_id (UUID):
        body (CreateToolRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateToolResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    data_product_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolRequest,
) -> CreateToolResponse | HTTPValidationError | None:
    """Create Tool

    Args:
        data_product_id (UUID):
        body (CreateToolRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateToolResponse | HTTPValidationError
    """

    return sync_detailed(
        data_product_id=data_product_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    data_product_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolRequest,
) -> Response[CreateToolResponse | HTTPValidationError]:
    """Create Tool

    Args:
        data_product_id (UUID):
        body (CreateToolRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CreateToolResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_product_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: CreateToolRequest,
) -> CreateToolResponse | HTTPValidationError | None:
    """Create Tool

    Args:
        data_product_id (UUID):
        body (CreateToolRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CreateToolResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            data_product_id=data_product_id,
            client=client,
            body=body,
        )
    ).parsed
