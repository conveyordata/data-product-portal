from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.decision_status import DecisionStatus
from ...models.http_validation_error import HTTPValidationError
from ...models.list_output_port_role_assignments_response import (
    ListOutputPortRoleAssignmentsResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    output_port_id: UUID | Unset = UNSET,
    user_id: UUID | Unset = UNSET,
    role_id: UUID | Unset = UNSET,
    decision: DecisionStatus | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_output_port_id: str | Unset = UNSET
    if not isinstance(output_port_id, Unset):
        json_output_port_id = str(output_port_id)
    params["output_port_id"] = json_output_port_id

    json_user_id: str | Unset = UNSET
    if not isinstance(user_id, Unset):
        json_user_id = str(user_id)
    params["user_id"] = json_user_id

    json_role_id: str | Unset = UNSET
    if not isinstance(role_id, Unset):
        json_role_id = str(role_id)
    params["role_id"] = json_role_id

    json_decision: str | Unset = UNSET
    if not isinstance(decision, Unset):
        json_decision = decision.value

    params["decision"] = json_decision

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/authz/role_assignments/output_port",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ListOutputPortRoleAssignmentsResponse | None:
    if response.status_code == 200:
        response_200 = ListOutputPortRoleAssignmentsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ListOutputPortRoleAssignmentsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    output_port_id: UUID | Unset = UNSET,
    user_id: UUID | Unset = UNSET,
    role_id: UUID | Unset = UNSET,
    decision: DecisionStatus | Unset = UNSET,
) -> Response[HTTPValidationError | ListOutputPortRoleAssignmentsResponse]:
    """List Output Port Role Assignments

    Args:
        output_port_id (UUID | Unset):
        user_id (UUID | Unset):
        role_id (UUID | Unset):
        decision (DecisionStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ListOutputPortRoleAssignmentsResponse]
    """

    kwargs = _get_kwargs(
        output_port_id=output_port_id,
        user_id=user_id,
        role_id=role_id,
        decision=decision,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    output_port_id: UUID | Unset = UNSET,
    user_id: UUID | Unset = UNSET,
    role_id: UUID | Unset = UNSET,
    decision: DecisionStatus | Unset = UNSET,
) -> HTTPValidationError | ListOutputPortRoleAssignmentsResponse | None:
    """List Output Port Role Assignments

    Args:
        output_port_id (UUID | Unset):
        user_id (UUID | Unset):
        role_id (UUID | Unset):
        decision (DecisionStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ListOutputPortRoleAssignmentsResponse
    """

    return sync_detailed(
        client=client,
        output_port_id=output_port_id,
        user_id=user_id,
        role_id=role_id,
        decision=decision,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    output_port_id: UUID | Unset = UNSET,
    user_id: UUID | Unset = UNSET,
    role_id: UUID | Unset = UNSET,
    decision: DecisionStatus | Unset = UNSET,
) -> Response[HTTPValidationError | ListOutputPortRoleAssignmentsResponse]:
    """List Output Port Role Assignments

    Args:
        output_port_id (UUID | Unset):
        user_id (UUID | Unset):
        role_id (UUID | Unset):
        decision (DecisionStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ListOutputPortRoleAssignmentsResponse]
    """

    kwargs = _get_kwargs(
        output_port_id=output_port_id,
        user_id=user_id,
        role_id=role_id,
        decision=decision,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    output_port_id: UUID | Unset = UNSET,
    user_id: UUID | Unset = UNSET,
    role_id: UUID | Unset = UNSET,
    decision: DecisionStatus | Unset = UNSET,
) -> HTTPValidationError | ListOutputPortRoleAssignmentsResponse | None:
    """List Output Port Role Assignments

    Args:
        output_port_id (UUID | Unset):
        user_id (UUID | Unset):
        role_id (UUID | Unset):
        decision (DecisionStatus | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ListOutputPortRoleAssignmentsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            output_port_id=output_port_id,
            user_id=user_id,
            role_id=role_id,
            decision=decision,
        )
    ).parsed
