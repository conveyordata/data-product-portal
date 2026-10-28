from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.revoke_input_port_for_exploration_response import (
    RevokeInputPortForExplorationResponse,
)
from ...types import Response


def _get_kwargs(
    id: UUID,
    output_port_id: UUID,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/explorations/{id}/input_ports/{output_port_id}/revoke".format(
            id=quote(str(id), safe=""),
            output_port_id=quote(str(output_port_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RevokeInputPortForExplorationResponse | None:
    if response.status_code == 200:
        response_200 = RevokeInputPortForExplorationResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | RevokeInputPortForExplorationResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: UUID,
    output_port_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | RevokeInputPortForExplorationResponse]:
    """Revoke Input Port For Exploration

    Args:
        id (UUID):
        output_port_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RevokeInputPortForExplorationResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        output_port_id=output_port_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: UUID,
    output_port_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | RevokeInputPortForExplorationResponse | None:
    """Revoke Input Port For Exploration

    Args:
        id (UUID):
        output_port_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RevokeInputPortForExplorationResponse
    """

    return sync_detailed(
        id=id,
        output_port_id=output_port_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: UUID,
    output_port_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> Response[HTTPValidationError | RevokeInputPortForExplorationResponse]:
    """Revoke Input Port For Exploration

    Args:
        id (UUID):
        output_port_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RevokeInputPortForExplorationResponse]
    """

    kwargs = _get_kwargs(
        id=id,
        output_port_id=output_port_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: UUID,
    output_port_id: UUID,
    *,
    client: AuthenticatedClient | Client,
) -> HTTPValidationError | RevokeInputPortForExplorationResponse | None:
    """Revoke Input Port For Exploration

    Args:
        id (UUID):
        output_port_id (UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RevokeInputPortForExplorationResponse
    """

    return (
        await asyncio_detailed(
            id=id,
            output_port_id=output_port_id,
            client=client,
        )
    ).parsed
