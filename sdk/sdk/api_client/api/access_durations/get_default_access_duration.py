from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.access_duration import AccessDuration
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    abstract_data_product_type: str,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/access_durations/{abstract_data_product_type}/default".format(
            abstract_data_product_type=quote(str(abstract_data_product_type), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccessDuration | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AccessDuration.from_dict(response.json())

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
) -> Response[AccessDuration | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    abstract_data_product_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AccessDuration | HTTPValidationError]:
    """Get Default Access Duration

    Args:
        abstract_data_product_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccessDuration | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        abstract_data_product_type=abstract_data_product_type,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    abstract_data_product_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> AccessDuration | HTTPValidationError | None:
    """Get Default Access Duration

    Args:
        abstract_data_product_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccessDuration | HTTPValidationError
    """

    return sync_detailed(
        abstract_data_product_type=abstract_data_product_type,
        client=client,
    ).parsed


async def asyncio_detailed(
    abstract_data_product_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[AccessDuration | HTTPValidationError]:
    """Get Default Access Duration

    Args:
        abstract_data_product_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccessDuration | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        abstract_data_product_type=abstract_data_product_type,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    abstract_data_product_type: str,
    *,
    client: AuthenticatedClient | Client,
) -> AccessDuration | HTTPValidationError | None:
    """Get Default Access Duration

    Args:
        abstract_data_product_type (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccessDuration | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            abstract_data_product_type=abstract_data_product_type,
            client=client,
        )
    ).parsed
