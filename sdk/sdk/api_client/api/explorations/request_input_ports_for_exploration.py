from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.request_input_ports_for_exploration_request import (
    RequestInputPortsForExplorationRequest,
)
from ...models.request_input_ports_for_exploration_response import (
    RequestInputPortsForExplorationResponse,
)
from ...types import Response


def _get_kwargs(
    id: UUID,
    *,
    body: RequestInputPortsForExplorationRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/explorations/{id}/input_ports".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RequestInputPortsForExplorationResponse | None:
    if response.status_code == 200:
        response_200 = RequestInputPortsForExplorationResponse.from_dict(
            response.json()
        )

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
) -> Response[HTTPValidationError | RequestInputPortsForExplorationResponse]:
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
    body: RequestInputPortsForExplorationRequest,
) -> Response[HTTPValidationError | RequestInputPortsForExplorationResponse]:
    """Request Input Ports For Exploration

    Args:
        id (UUID):
        body (RequestInputPortsForExplorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RequestInputPortsForExplorationResponse]
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
    body: RequestInputPortsForExplorationRequest,
) -> HTTPValidationError | RequestInputPortsForExplorationResponse | None:
    """Request Input Ports For Exploration

    Args:
        id (UUID):
        body (RequestInputPortsForExplorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RequestInputPortsForExplorationResponse
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
    body: RequestInputPortsForExplorationRequest,
) -> Response[HTTPValidationError | RequestInputPortsForExplorationResponse]:
    """Request Input Ports For Exploration

    Args:
        id (UUID):
        body (RequestInputPortsForExplorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RequestInputPortsForExplorationResponse]
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
    body: RequestInputPortsForExplorationRequest,
) -> HTTPValidationError | RequestInputPortsForExplorationResponse | None:
    """Request Input Ports For Exploration

    Args:
        id (UUID):
        body (RequestInputPortsForExplorationRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RequestInputPortsForExplorationResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
