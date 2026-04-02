from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_product_role_assignment_response import (
    DataProductRoleAssignmentResponse,
)
from ...models.decide_data_product_role_assignment import (
    DecideDataProductRoleAssignment,
)
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    id: UUID,
    *,
    body: DecideDataProductRoleAssignment,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/authz/role_assignments/data_product/{id}/decide".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DataProductRoleAssignmentResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DataProductRoleAssignmentResponse.from_dict(response.json())

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
) -> Response[DataProductRoleAssignmentResponse | HTTPValidationError]:
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
    body: DecideDataProductRoleAssignment,
) -> Response[DataProductRoleAssignmentResponse | HTTPValidationError]:
    """Decide Data Product Role Assignment

    Args:
        id (UUID):
        body (DecideDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataProductRoleAssignmentResponse | HTTPValidationError]
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
    body: DecideDataProductRoleAssignment,
) -> DataProductRoleAssignmentResponse | HTTPValidationError | None:
    """Decide Data Product Role Assignment

    Args:
        id (UUID):
        body (DecideDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataProductRoleAssignmentResponse | HTTPValidationError
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
    body: DecideDataProductRoleAssignment,
) -> Response[DataProductRoleAssignmentResponse | HTTPValidationError]:
    """Decide Data Product Role Assignment

    Args:
        id (UUID):
        body (DecideDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataProductRoleAssignmentResponse | HTTPValidationError]
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
    body: DecideDataProductRoleAssignment,
) -> DataProductRoleAssignmentResponse | HTTPValidationError | None:
    """Decide Data Product Role Assignment

    Args:
        id (UUID):
        body (DecideDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataProductRoleAssignmentResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
