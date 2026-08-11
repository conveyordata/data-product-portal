"""MCP resources for data products, output ports, and marketplace."""

from uuid import UUID

from fastmcp.dependencies import Depends
from sqlalchemy.orm import Session

from app.configuration.domains.service import DomainService
from app.data_products.output_ports.schema_response import GetOutputPortResponse
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_response import GetDataProductResponse
from app.data_products.service import DataProductService
from app.data_products.technical_assets.service import TechnicalAssetService
from app.mcp.deps import get_db_session, get_mcp_authenticated_user
from app.users.model import User as UserModel


def register_resources(mcp) -> None:
    @mcp.resource(
        "data-product://{data_product_id}",
        description="""Get data product as a resource.""",
    )
    def get_data_product_resource(
        data_product_id: str, db: Session = Depends(get_db_session)
    ) -> str:
        data_product = DataProductService(db).get_data_product(
            id=UUID(data_product_id),
        )

        if not data_product:
            return f"Error: Data product {data_product_id} not found"

        dp_data = GetDataProductResponse.model_validate(data_product)

        return f"""
# Data Product: {dp_data.name}

**ID:** {dp_data.id}
**Status:** {dp_data.status}
**Domain:** {dp_data.domain.name if dp_data.domain else "N/A"}
**Description:** {dp_data.description or "No description available"}

## Metadata
- **Created:** {dp_data.created_at}
- **Updated:** {dp_data.updated_at}
- **Owner:** {dp_data.owner_email or "N/A"}

"""

    @mcp.resource(
        "output-port://{output_port_id}",
        description="""Get output port as a resource.""",
    )
    def get_output_port_resource(
        output_port_id: str,
        db: Session = Depends(get_db_session),
        user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> str:
        output_port = OutputPortService(db).get_output_port(
            id=UUID(output_port_id), user=user
        )

        if not output_port:
            return f"Error: Output port {output_port_id} not found"

        ds_data = GetOutputPortResponse.model_validate(output_port)

        return f"""
# Output port: {ds_data.name}

**ID:** {ds_data.id}
**Status:** {ds_data.status}
**Description:** {ds_data.description or "No description available"}

## Metadata
- **Created:** {ds_data.created_at}
- **Updated:** {ds_data.updated_at}
- **Owner:** {ds_data.owner_email or "N/A"}

## Data Product
**ID:** {ds_data.data_product_id}
**Name:** {ds_data.data_product_name}
"""

    @mcp.resource(
        "marketplace://overview",
        description="""Get marketplace overview as a resource.""",
    )
    def get_marketplace_resource(
        db: Session = Depends(get_db_session),
        user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> str:
        all_data_products = DataProductService(db).get_data_products()
        all_output_ports = OutputPortService(db).search_output_ports(
            query=None, limit=1000, user=user, current_user_assigned=False
        )
        all_technical_assets = TechnicalAssetService(db).get_data_outputs()
        all_domains = DomainService(db).get_domains()

        stats = {
            "total_data_products": len(all_data_products),
            "total_output_ports": len(all_output_ports),
            "total_technical_assets": len(all_technical_assets),
            "total_domains": len(all_domains),
        }

        return f"""
# Data Product Portal - Marketplace Overview

## Statistics
- **Data Products:** {stats["total_data_products"]}
- **Output Ports:** {stats["total_output_ports"]}
- **Technical Assets:** {stats["total_technical_assets"]}
- **Domains:** {stats["total_domains"]}
"""
