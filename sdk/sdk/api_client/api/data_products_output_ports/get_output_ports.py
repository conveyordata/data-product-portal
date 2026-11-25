from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.assignment_filter import AssignmentFilter
from ...models.get_output_ports_response import GetOutputPortsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    assignment_filter: AssignmentFilter | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_assignment_filter: str | Unset = UNSET
    if not isinstance(assignment_filter, Unset):
        json_assignment_filter = assignment_filter.value

    params["assignment_filter"] = json_assignment_filter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/output_ports",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetOutputPortsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = GetOutputPortsResponse.from_dict(response.json())

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
) -> Response[GetOutputPortsResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    assignment_filter: AssignmentFilter | Unset = UNSET,
) -> Response[GetOutputPortsResponse | HTTPValidationError]:
    """Get Output Ports

    Args:
        assignment_filter (AssignmentFilter | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOutputPortsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        assignment_filter=assignment_filter,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    assignment_filter: AssignmentFilter | Unset = UNSET,
) -> GetOutputPortsResponse | HTTPValidationError | None:
    """Get Output Ports

    Args:
        assignment_filter (AssignmentFilter | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOutputPortsResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        assignment_filter=assignment_filter,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    assignment_filter: AssignmentFilter | Unset = UNSET,
) -> Response[GetOutputPortsResponse | HTTPValidationError]:
    """Get Output Ports

    Args:
        assignment_filter (AssignmentFilter | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetOutputPortsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        assignment_filter=assignment_filter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    assignment_filter: AssignmentFilter | Unset = UNSET,
) -> GetOutputPortsResponse | HTTPValidationError | None:
    """Get Output Ports

    Args:
        assignment_filter (AssignmentFilter | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetOutputPortsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            assignment_filter=assignment_filter,
        )
    ).parsed
