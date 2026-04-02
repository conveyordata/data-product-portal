from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote
from uuid import UUID

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.output_port_data_quality_summary import OutputPortDataQualitySummary
from ...models.output_port_data_quality_summary_response import (
    OutputPortDataQualitySummaryResponse,
)
from ...types import Response


def _get_kwargs(
    data_product_id: UUID,
    id: UUID,
    summary_id: UUID,
    *,
    body: OutputPortDataQualitySummary,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v2/data_products/{data_product_id}/output_ports/{id}/data_quality_summary/{summary_id}".format(
            data_product_id=quote(str(data_product_id), safe=""),
            id=quote(str(id), safe=""),
            summary_id=quote(str(summary_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | OutputPortDataQualitySummaryResponse | None:
    if response.status_code == 200:
        response_200 = OutputPortDataQualitySummaryResponse.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError | OutputPortDataQualitySummaryResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    data_product_id: UUID,
    id: UUID,
    summary_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: OutputPortDataQualitySummary,
) -> Response[Any | HTTPValidationError | OutputPortDataQualitySummaryResponse]:
    """Overwrite Output Port Data Quality Summary

    Args:
        data_product_id (UUID):
        id (UUID):
        summary_id (UUID):
        body (OutputPortDataQualitySummary):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | OutputPortDataQualitySummaryResponse]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        summary_id=summary_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    data_product_id: UUID,
    id: UUID,
    summary_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: OutputPortDataQualitySummary,
) -> Any | HTTPValidationError | OutputPortDataQualitySummaryResponse | None:
    """Overwrite Output Port Data Quality Summary

    Args:
        data_product_id (UUID):
        id (UUID):
        summary_id (UUID):
        body (OutputPortDataQualitySummary):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | OutputPortDataQualitySummaryResponse
    """

    return sync_detailed(
        data_product_id=data_product_id,
        id=id,
        summary_id=summary_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    data_product_id: UUID,
    id: UUID,
    summary_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: OutputPortDataQualitySummary,
) -> Response[Any | HTTPValidationError | OutputPortDataQualitySummaryResponse]:
    """Overwrite Output Port Data Quality Summary

    Args:
        data_product_id (UUID):
        id (UUID):
        summary_id (UUID):
        body (OutputPortDataQualitySummary):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | OutputPortDataQualitySummaryResponse]
    """

    kwargs = _get_kwargs(
        data_product_id=data_product_id,
        id=id,
        summary_id=summary_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    data_product_id: UUID,
    id: UUID,
    summary_id: UUID,
    *,
    client: AuthenticatedClient | Client,
    body: OutputPortDataQualitySummary,
) -> Any | HTTPValidationError | OutputPortDataQualitySummaryResponse | None:
    """Overwrite Output Port Data Quality Summary

    Args:
        data_product_id (UUID):
        id (UUID):
        summary_id (UUID):
        body (OutputPortDataQualitySummary):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | OutputPortDataQualitySummaryResponse
    """

    return (
        await asyncio_detailed(
            data_product_id=data_product_id,
            id=id,
            summary_id=summary_id,
            client=client,
            body=body,
        )
    ).parsed
