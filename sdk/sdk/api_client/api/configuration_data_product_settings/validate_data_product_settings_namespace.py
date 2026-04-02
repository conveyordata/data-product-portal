from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_product_setting_scope import DataProductSettingScope
from ...models.http_validation_error import HTTPValidationError
from ...models.namespace_validation import NamespaceValidation
from ...types import UNSET, Response


def _get_kwargs(
    *,
    namespace: str,
    scope: DataProductSettingScope,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["namespace"] = namespace

    json_scope = scope.value
    params["scope"] = json_scope

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/configuration/data_product_settings/validate_namespace",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | NamespaceValidation | None:
    if response.status_code == 200:
        response_200 = NamespaceValidation.from_dict(response.json())

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
) -> Response[HTTPValidationError | NamespaceValidation]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    namespace: str,
    scope: DataProductSettingScope,
) -> Response[HTTPValidationError | NamespaceValidation]:
    """Validate Data Product Settings Namespace

    Args:
        namespace (str):
        scope (DataProductSettingScope):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NamespaceValidation]
    """

    kwargs = _get_kwargs(
        namespace=namespace,
        scope=scope,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    namespace: str,
    scope: DataProductSettingScope,
) -> HTTPValidationError | NamespaceValidation | None:
    """Validate Data Product Settings Namespace

    Args:
        namespace (str):
        scope (DataProductSettingScope):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NamespaceValidation
    """

    return sync_detailed(
        client=client,
        namespace=namespace,
        scope=scope,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    namespace: str,
    scope: DataProductSettingScope,
) -> Response[HTTPValidationError | NamespaceValidation]:
    """Validate Data Product Settings Namespace

    Args:
        namespace (str):
        scope (DataProductSettingScope):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | NamespaceValidation]
    """

    kwargs = _get_kwargs(
        namespace=namespace,
        scope=scope,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    namespace: str,
    scope: DataProductSettingScope,
) -> HTTPValidationError | NamespaceValidation | None:
    """Validate Data Product Settings Namespace

    Args:
        namespace (str):
        scope (DataProductSettingScope):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | NamespaceValidation
    """

    return (
        await asyncio_detailed(
            client=client,
            namespace=namespace,
            scope=scope,
        )
    ).parsed
