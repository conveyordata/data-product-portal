"""Tools for retrieving detailed information about data products, output ports, and technical assets."""

from typing import Any
from uuid import UUID

from fastmcp.dependencies import Depends
from sqlalchemy.orm import Session

from app.configuration.domains.schema_response import GetDomainResponse
from app.configuration.domains.service import DomainService
from app.data_products.output_ports.schema_response import GetOutputPortResponse
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_response import GetDataProductResponse
from app.data_products.service import DataProductService
from app.data_products.technical_assets.model import ensure_technical_asset_exists
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)
from app.data_products.technical_assets.service import TechnicalAssetService
from app.mcp.deps import get_db_session, get_mcp_authenticated_user
from app.users.model import User as UserModel


def get_data_product_details(
    data_product_id: str,
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    data_product = DataProductService(db).get_data_product(
        id=UUID(data_product_id),
    )
    return GetDataProductResponse.model_validate(data_product).model_dump()


def get_output_port_details(
    output_port_id: str,
    db: Session = Depends(get_db_session),
    user: UserModel = Depends(get_mcp_authenticated_user),
) -> dict[str, Any]:
    dataset = OutputPortService(db).get_output_port(id=UUID(output_port_id), user=user)
    return GetOutputPortResponse.model_validate(dataset).model_dump()


def get_technical_asset_details(
    technical_asset_id: str,
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    do = ensure_technical_asset_exists(UUID(technical_asset_id), db=db)
    data_output = TechnicalAssetService(db).get_technical_asset(
        do.owner_id,
        id=UUID(technical_asset_id),
    )
    return GetTechnicalAssetsResponseItem.model_validate(data_output).model_dump()


def get_domain_details(
    domain_id: str, db: Session = Depends(get_db_session)
) -> dict[str, Any]:
    domain = DomainService(db).get_domain(
        id=UUID(domain_id),
    )
    return GetDomainResponse.model_validate(domain).model_dump()


def register_detail_tools(mcp) -> None:
    mcp.tool(
        description="""
    Get full details of a single data product by its UUID, including its description,
    domain, lifecycle status, owners, output ports, and technical assets.
    Use after search_data_products or search_output_ports to drill into a related data product.

    Args:
        data_product_id: UUID obtained from search_data_products or universal_search.
    """
    )(get_data_product_details)

    mcp.tool(
        description="""
    Get full details of a single output port by its UUID, including schema, access type,
    the data product it belongs to, and owner contact information.
    Use after search_output_ports to get complete information about a specific dataset.

    CRITICAL FOR DATA QUERIES: This returns data_product_links[], which contains the consuming
    data products that have access to this output port. These are typically YOUR access path to
    query the data. Extract the namespace from each data_product_links[].data_product.namespace
    and try those FIRST when getting credentials.

    Also returns data_output_links[] with technical_asset configuration including the database name.

    Args:
        output_port_id: UUID obtained from search_output_ports or universal_search.

    Returns:
        - data_product_links: List of consuming data products (YOUR access path!)
        - data_output_links: Technical assets with database configuration
        - namespace: Owner data product namespace (try as fallback only)
    """
    )(get_output_port_details)

    mcp.tool(
        description="""
    Get full details of a specific technical asset (data output) by its UUID,
    including its type, configuration, and the data product it belongs to.

    Args:
        technical_asset_id: UUID obtained from universal_search or get_data_product_analytics.
    """
    )(get_technical_asset_details)

    mcp.tool(
        description="""
    Get details of a specific domain by its UUID, including its name and description.
    Use get_marketplace_overview first to discover available domain IDs.

    Args:
        domain_id: UUID obtained from get_marketplace_overview or search results.
    """
    )(get_domain_details)
