from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_product_role_assignment_response import (
    DataProductRoleAssignmentResponse,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.request_data_product_role_assignment import (
    RequestDataProductRoleAssignment,
)
from ...types import Response


def _get_kwargs(
    *,
    body: RequestDataProductRoleAssignment,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v2/authz/role_assignments/data_product/request",
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
    *,
    client: AuthenticatedClient | Client,
    body: RequestDataProductRoleAssignment,
) -> Response[DataProductRoleAssignmentResponse | HTTPValidationError]:
    """Request Data Product Role Assignment

    Args:
        body (RequestDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataProductRoleAssignmentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: RequestDataProductRoleAssignment,
) -> DataProductRoleAssignmentResponse | HTTPValidationError | None:
    """Request Data Product Role Assignment

    Args:
        body (RequestDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataProductRoleAssignmentResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: RequestDataProductRoleAssignment,
) -> Response[DataProductRoleAssignmentResponse | HTTPValidationError]:
    """Request Data Product Role Assignment

    Args:
        body (RequestDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DataProductRoleAssignmentResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: RequestDataProductRoleAssignment,
) -> DataProductRoleAssignmentResponse | HTTPValidationError | None:
    """Request Data Product Role Assignment

    Args:
        body (RequestDataProductRoleAssignment):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DataProductRoleAssignmentResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
