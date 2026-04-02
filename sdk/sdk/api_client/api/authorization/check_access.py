from http import HTTPStatus
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.access_response import AccessResponse
from ...models.authorization_action import AuthorizationAction
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    action: AuthorizationAction,
    *,
    resource: None | Unset | UUID = UNSET,
    domain: None | Unset | UUID = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_resource: None | str | Unset
    if isinstance(resource, Unset):
        json_resource = UNSET
    elif isinstance(resource, UUID):
        json_resource = str(resource)
    else:
        json_resource = resource
    params["resource"] = json_resource

    json_domain: None | str | Unset
    if isinstance(domain, Unset):
        json_domain = UNSET
    elif isinstance(domain, UUID):
        json_domain = str(domain)
    else:
        json_domain = domain
    params["domain"] = json_domain

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v2/authz/access/{action}".format(
            action=quote(str(action), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> AccessResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = AccessResponse.from_dict(response.json())

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
) -> Response[AccessResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    action: AuthorizationAction,
    *,
    client: AuthenticatedClient | Client,
    resource: None | Unset | UUID = UNSET,
    domain: None | Unset | UUID = UNSET,
) -> Response[AccessResponse | HTTPValidationError]:
    """Check Access

     Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.

    Args:
        action (AuthorizationAction): The integer values for the authorization actions are stored
            directly in the DB.
            This means you can change the name of the actions, but not their integer values.
            The values for the actions are spaced on purpose, to make it easier to extend.
            This has no technical benefit, but it makes it easier to read for developers.
        resource (None | Unset | UUID):
        domain (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccessResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        action=action,
        resource=resource,
        domain=domain,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    action: AuthorizationAction,
    *,
    client: AuthenticatedClient | Client,
    resource: None | Unset | UUID = UNSET,
    domain: None | Unset | UUID = UNSET,
) -> AccessResponse | HTTPValidationError | None:
    """Check Access

     Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.

    Args:
        action (AuthorizationAction): The integer values for the authorization actions are stored
            directly in the DB.
            This means you can change the name of the actions, but not their integer values.
            The values for the actions are spaced on purpose, to make it easier to extend.
            This has no technical benefit, but it makes it easier to read for developers.
        resource (None | Unset | UUID):
        domain (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccessResponse | HTTPValidationError
    """

    return sync_detailed(
        action=action,
        client=client,
        resource=resource,
        domain=domain,
    ).parsed


async def asyncio_detailed(
    action: AuthorizationAction,
    *,
    client: AuthenticatedClient | Client,
    resource: None | Unset | UUID = UNSET,
    domain: None | Unset | UUID = UNSET,
) -> Response[AccessResponse | HTTPValidationError]:
    """Check Access

     Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.

    Args:
        action (AuthorizationAction): The integer values for the authorization actions are stored
            directly in the DB.
            This means you can change the name of the actions, but not their integer values.
            The values for the actions are spaced on purpose, to make it easier to extend.
            This has no technical benefit, but it makes it easier to read for developers.
        resource (None | Unset | UUID):
        domain (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[AccessResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        action=action,
        resource=resource,
        domain=domain,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    action: AuthorizationAction,
    *,
    client: AuthenticatedClient | Client,
    resource: None | Unset | UUID = UNSET,
    domain: None | Unset | UUID = UNSET,
) -> AccessResponse | HTTPValidationError | None:
    """Check Access

     Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.

    Args:
        action (AuthorizationAction): The integer values for the authorization actions are stored
            directly in the DB.
            This means you can change the name of the actions, but not their integer values.
            The values for the actions are spaced on purpose, to make it easier to extend.
            This has no technical benefit, but it makes it easier to read for developers.
        resource (None | Unset | UUID):
        domain (None | Unset | UUID):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        AccessResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            action=action,
            client=client,
            resource=resource,
            domain=domain,
        )
    ).parsed
