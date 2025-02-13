from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.aws_credentials import AWSCredentials
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response


def _get_kwargs(
    *,
    data_product_name: str,
    environment: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["data_product_name"] = data_product_name

    params["environment"] = environment

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/auth/aws_credentials",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[AWSCredentials, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = AWSCredentials.from_dict(response.json())

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[AWSCredentials, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    data_product_name: str,
    environment: str,
) -> Response[Union[AWSCredentials, HTTPValidationError]]:
    """Get Aws Credentials

    Args:
        data_product_name (str):
        environment (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AWSCredentials, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        data_product_name=data_product_name,
        environment=environment,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    data_product_name: str,
    environment: str,
) -> Optional[Union[AWSCredentials, HTTPValidationError]]:
    """Get Aws Credentials

    Args:
        data_product_name (str):
        environment (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AWSCredentials, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        data_product_name=data_product_name,
        environment=environment,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    data_product_name: str,
    environment: str,
) -> Response[Union[AWSCredentials, HTTPValidationError]]:
    """Get Aws Credentials

    Args:
        data_product_name (str):
        environment (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[AWSCredentials, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        data_product_name=data_product_name,
        environment=environment,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    data_product_name: str,
    environment: str,
) -> Optional[Union[AWSCredentials, HTTPValidationError]]:
    """Get Aws Credentials

    Args:
        data_product_name (str):
        environment (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[AWSCredentials, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            data_product_name=data_product_name,
            environment=environment,
        )
    ).parsed
