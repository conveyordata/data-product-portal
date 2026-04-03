from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.decision_status import DecisionStatus
from ...models.http_validation_error import HTTPValidationError
from ...models.list_data_product_role_assignments_response import (
    ListDataProductRoleAssignmentsResponse,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    data_product_id: None | Unset | UUID = UNSET,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
    decision: DecisionStatus | None | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_data_product_id: None | str | Unset
    if isinstance(data_product_id, Unset):
        json_data_product_id = UNSET
    elif isinstance(data_product_id, UUID):
        json_data_product_id = str(data_product_id)
    else:
        json_data_product_id = data_product_id
    params["data_product_id"] = json_data_product_id

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

    json_decision: None | str | Unset
    if isinstance(decision, Unset):
        json_decision = UNSET
    elif isinstance(decision, DecisionStatus):
        json_decision = decision.value
    else:
        json_decision = decision
    params["decision"] = json_decision

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/authz/role_assignments/data_product",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ListDataProductRoleAssignmentsResponse | None:
    if response.status_code == 200:
        response_200 = ListDataProductRoleAssignmentsResponse.from_dict(response.json())

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
) -> Response[HTTPValidationError | ListDataProductRoleAssignmentsResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    data_product_id: None | Unset | UUID = UNSET,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
    decision: DecisionStatus | None | Unset = UNSET,
) -> Response[HTTPValidationError | ListDataProductRoleAssignmentsResponse]:
    """List Data Product Role Assignments

    Args:
        data_product_id (None | Unset | UUID):
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):
        decision (DecisionStatus | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ListDataProductRoleAssignmentsResponse]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
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
    data_product_id: None | Unset | UUID = UNSET,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
    decision: DecisionStatus | None | Unset = UNSET,
) -> HTTPValidationError | ListDataProductRoleAssignmentsResponse | None:
    """List Data Product Role Assignments

    Args:
        data_product_id (None | Unset | UUID):
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):
        decision (DecisionStatus | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ListDataProductRoleAssignmentsResponse
    """

    return sync_detailed(
        client=client,
        data_product_id=data_product_id,
        user_id=user_id,
        role_id=role_id,
        decision=decision,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    data_product_id: None | Unset | UUID = UNSET,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
    decision: DecisionStatus | None | Unset = UNSET,
) -> Response[HTTPValidationError | ListDataProductRoleAssignmentsResponse]:
    """List Data Product Role Assignments

    Args:
        data_product_id (None | Unset | UUID):
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):
        decision (DecisionStatus | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ListDataProductRoleAssignmentsResponse]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        user_id=user_id,
        role_id=role_id,
        decision=decision,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    data_product_id: None | Unset | UUID = UNSET,
    user_id: None | Unset | UUID = UNSET,
    role_id: None | Unset | UUID = UNSET,
    decision: DecisionStatus | None | Unset = UNSET,
) -> HTTPValidationError | ListDataProductRoleAssignmentsResponse | None:
    """List Data Product Role Assignments

    Args:
        data_product_id (None | Unset | UUID):
        user_id (None | Unset | UUID):
        role_id (None | Unset | UUID):
        decision (DecisionStatus | None | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ListDataProductRoleAssignmentsResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            data_product_id=data_product_id,
            user_id=user_id,
            role_id=role_id,
            decision=decision,
        )
    ).parsed
