from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_data_products_response import GetDataProductsResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    filter_to_user_with_assigment: None | Unset | UUID = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_filter_to_user_with_assigment: None | str | Unset
    if isinstance(filter_to_user_with_assigment, Unset):
        json_filter_to_user_with_assigment = UNSET
    elif isinstance(filter_to_user_with_assigment, UUID):
        json_filter_to_user_with_assigment = str(filter_to_user_with_assigment)
    else:
        json_filter_to_user_with_assigment = filter_to_user_with_assigment
    params["filter_to_user_with_assigment"] = json_filter_to_user_with_assigment

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/data_products",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> GetDataProductsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = GetDataProductsResponse.from_dict(response.json())

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
) -> Response[GetDataProductsResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    filter_to_user_with_assigment: None | Unset | UUID = UNSET,
) -> Response[GetDataProductsResponse | HTTPValidationError]:
    """Get Data Products

    Args:
        filter_to_user_with_assigment (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDataProductsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        filter_to_user_with_assigment=filter_to_user_with_assigment,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    filter_to_user_with_assigment: None | Unset | UUID = UNSET,
) -> GetDataProductsResponse | HTTPValidationError | None:
    """Get Data Products

    Args:
        filter_to_user_with_assigment (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDataProductsResponse | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        filter_to_user_with_assigment=filter_to_user_with_assigment,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    filter_to_user_with_assigment: None | Unset | UUID = UNSET,
) -> Response[GetDataProductsResponse | HTTPValidationError]:
    """Get Data Products

    Args:
        filter_to_user_with_assigment (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[GetDataProductsResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        filter_to_user_with_assigment=filter_to_user_with_assigment,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    filter_to_user_with_assigment: None | Unset | UUID = UNSET,
) -> GetDataProductsResponse | HTTPValidationError | None:
    """Get Data Products

    Args:
        filter_to_user_with_assigment (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        GetDataProductsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            filter_to_user_with_assigment=filter_to_user_with_assigment,
        )
    ).parsed
