from http import HTTPStatus
from typing import Any
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.resource_name_model import ResourceNameModel
from ...models.resource_name_validation import ResourceNameValidation
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    resource_name: str,
    model: ResourceNameModel,
    data_product_id: UUID | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["resource_name"] = resource_name

    json_model = model.value
    params["model"] = json_model

    json_data_product_id: str | Unset = UNSET
    if not isinstance(data_product_id, Unset):
        json_data_product_id = str(data_product_id)
    params["data_product_id"] = json_data_product_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/resource_names/validate",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ResourceNameValidation | None:
    if response.status_code == 200:
        response_200 = ResourceNameValidation.from_dict(response.json())

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
) -> Response[HTTPValidationError | ResourceNameValidation]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    resource_name: str,
    model: ResourceNameModel,
    data_product_id: UUID | Unset = UNSET,
) -> Response[HTTPValidationError | ResourceNameValidation]:
    """Validate Resource Name

    Args:
        resource_name (str):
        model (ResourceNameModel):
        data_product_id (UUID | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResourceNameValidation]
    """

    kwargs = _get_kwargs(
        resource_name=resource_name,
        model=model,
        data_product_id=data_product_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    resource_name: str,
    model: ResourceNameModel,
    data_product_id: UUID | Unset = UNSET,
) -> HTTPValidationError | ResourceNameValidation | None:
    """Validate Resource Name

    Args:
        resource_name (str):
        model (ResourceNameModel):
        data_product_id (UUID | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResourceNameValidation
    """

    return sync_detailed(
        client=client,
        resource_name=resource_name,
        model=model,
        data_product_id=data_product_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    resource_name: str,
    model: ResourceNameModel,
    data_product_id: UUID | Unset = UNSET,
) -> Response[HTTPValidationError | ResourceNameValidation]:
    """Validate Resource Name

    Args:
        resource_name (str):
        model (ResourceNameModel):
        data_product_id (UUID | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ResourceNameValidation]
    """

    kwargs = _get_kwargs(
        resource_name=resource_name,
        model=model,
        data_product_id=data_product_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    resource_name: str,
    model: ResourceNameModel,
    data_product_id: UUID | Unset = UNSET,
) -> HTTPValidationError | ResourceNameValidation | None:
    """Validate Resource Name

    Args:
        resource_name (str):
        model (ResourceNameModel):
        data_product_id (UUID | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ResourceNameValidation
    """

    return (
        await asyncio_detailed(
            client=client,
            resource_name=resource_name,
            model=model,
            data_product_id=data_product_id,
        )
    ).parsed
