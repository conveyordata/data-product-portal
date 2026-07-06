from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.abstract_data_product_type import AbstractDataProductType
from ...models.access_duration import AccessDuration
from ...models.access_duration_update import AccessDurationUpdate
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    abstract_data_product_type: AbstractDataProductType,
    *,
    body: AccessDurationUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v2/access_durations/{abstract_data_product_type}".format(
            abstract_data_product_type=quote(str(abstract_data_product_type), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[AccessDuration] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = AccessDuration.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[AccessDuration]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    abstract_data_product_type: AbstractDataProductType,
    *,
    client: AuthenticatedClient | Client,
    body: AccessDurationUpdate,
) -> Response[HTTPValidationError | list[AccessDuration]]:
    """Update Access Duration

    Args:
        abstract_data_product_type (AbstractDataProductType):
        body (AccessDurationUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[AccessDuration]]
    """

    kwargs = _get_kwargs(
        abstract_data_product_type=abstract_data_product_type,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    abstract_data_product_type: AbstractDataProductType,
    *,
    client: AuthenticatedClient | Client,
    body: AccessDurationUpdate,
) -> HTTPValidationError | list[AccessDuration] | None:
    """Update Access Duration

    Args:
        abstract_data_product_type (AbstractDataProductType):
        body (AccessDurationUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[AccessDuration]
    """

    return sync_detailed(
        abstract_data_product_type=abstract_data_product_type,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    abstract_data_product_type: AbstractDataProductType,
    *,
    client: AuthenticatedClient | Client,
    body: AccessDurationUpdate,
) -> Response[HTTPValidationError | list[AccessDuration]]:
    """Update Access Duration

    Args:
        abstract_data_product_type (AbstractDataProductType):
        body (AccessDurationUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[AccessDuration]]
    """

    kwargs = _get_kwargs(
        abstract_data_product_type=abstract_data_product_type,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    abstract_data_product_type: AbstractDataProductType,
    *,
    client: AuthenticatedClient | Client,
    body: AccessDurationUpdate,
) -> HTTPValidationError | list[AccessDuration] | None:
    """Update Access Duration

    Args:
        abstract_data_product_type (AbstractDataProductType):
        body (AccessDurationUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[AccessDuration]
    """

    return (
        await asyncio_detailed(
            abstract_data_product_type=abstract_data_product_type,
            client=client,
            body=body,
        )
    ).parsed
