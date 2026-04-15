from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.list_global_role_assignments_response import (
    ListGlobalRoleAssignmentsResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_user_id: None | str | Unset
    if isinstance(user_id, Unset):
        json_user_id = UNSET
    elif isinstance(user_id, UUID):
        json_user_id = str(user_id)
    else:
        json_user_id = user_id
    params["user_id"] = json_user_id

    json_role_id: None | str | Unset
    if isinstance(role_id, Unset):
        json_role_id = UNSET
    elif isinstance(role_id, UUID):
        json_role_id = str(role_id)
    else:
        json_role_id = role_id
    params["role_id"] = json_role_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/authz/role_assignments/global",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ListGlobalRoleAssignmentsResponse | None:
    if response.status_code == 200:
        response_200 = ListGlobalRoleAssignmentsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ListGlobalRoleAssignmentsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
) -> Response[HTTPValidationError | ListGlobalRoleAssignmentsResponse]:
    """List Global Role Assignments

    Args:
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ListGlobalRoleAssignmentsResponse]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        role_id=role_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
) -> HTTPValidationError | ListGlobalRoleAssignmentsResponse | None:
    """List Global Role Assignments

    Args:
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ListGlobalRoleAssignmentsResponse
    """

    return sync_detailed(
        client=client,
        user_id=user_id,
        role_id=role_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
) -> Response[HTTPValidationError | ListGlobalRoleAssignmentsResponse]:
    """List Global Role Assignments

    Args:
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ListGlobalRoleAssignmentsResponse]
    """

    kwargs = _get_kwargs(
        user_id=user_id,
        role_id=role_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
) -> HTTPValidationError | ListGlobalRoleAssignmentsResponse | None:
    """List Global Role Assignments

    Args:
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ListGlobalRoleAssignmentsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            user_id=user_id,
            role_id=role_id,
        )
    ).parsed
