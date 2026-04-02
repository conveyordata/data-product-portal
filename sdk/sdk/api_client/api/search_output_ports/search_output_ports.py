from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.search_output_ports_response import SearchOutputPortsResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    query: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    current_user_assigned: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_query: None | str | Unset
    if isinstance(query, Unset):
        json_query = UNSET
    else:
        json_query = query
    params["query"] = json_query

    params["limit"] = limit

    params["current_user_assigned"] = current_user_assigned

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/search/output_ports",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | SearchOutputPortsResponse | None:
    if response.status_code == 200:
        response_200 = SearchOutputPortsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | SearchOutputPortsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    query: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    current_user_assigned: bool | Unset = False,
) -> Response[HTTPValidationError | SearchOutputPortsResponse]:
    """Search Output Ports

    Args:
        query (None | str | Unset):
        limit (int | Unset):  Default: 100.
        current_user_assigned (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SearchOutputPortsResponse]
    """

    kwargs = _get_kwargs(
        query=query,
        limit=limit,
        current_user_assigned=current_user_assigned,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    query: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    current_user_assigned: bool | Unset = False,
) -> HTTPValidationError | SearchOutputPortsResponse | None:
    """Search Output Ports

    Args:
        query (None | str | Unset):
        limit (int | Unset):  Default: 100.
        current_user_assigned (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SearchOutputPortsResponse
    """

    return sync_detailed(
        client=client,
        query=query,
        limit=limit,
        current_user_assigned=current_user_assigned,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    query: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    current_user_assigned: bool | Unset = False,
) -> Response[HTTPValidationError | SearchOutputPortsResponse]:
    """Search Output Ports

    Args:
        query (None | str | Unset):
        limit (int | Unset):  Default: 100.
        current_user_assigned (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | SearchOutputPortsResponse]
    """

    kwargs = _get_kwargs(
        query=query,
        limit=limit,
        current_user_assigned=current_user_assigned,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    query: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    current_user_assigned: bool | Unset = False,
) -> HTTPValidationError | SearchOutputPortsResponse | None:
    """Search Output Ports

    Args:
        query (None | str | Unset):
        limit (int | Unset):  Default: 100.
        current_user_assigned (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | SearchOutputPortsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            query=query,
            limit=limit,
            current_user_assigned=current_user_assigned,
        )
    ).parsed
