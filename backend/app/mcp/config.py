"""Tools for marketplace overview, environments, and data product analytics."""

from typing import Any, Dict
from uuid import UUID

from fastmcp.dependencies import Depends
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import AssignmentFilter
from app.configuration.domains.schema_response import GetDomainsItem
from app.configuration.domains.service import DomainService
from app.configuration.environments.schema_response import EnvironmentGetItem
from app.configuration.environments.service import EnvironmentService
from app.data_products.output_ports.schema import OutputPort
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_response import (
    GetDataProductResponse,
    GetDataProductsResponseItem,
)
from app.data_products.service import DataProductService
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)
from app.data_products.technical_assets.service import TechnicalAssetService
from app.mcp.deps import get_db_session, get_mcp_authenticated_user
from app.search_output_ports.schema_response import SearchOutputPortsResponseItem
from app.users.model import User as UserModel


def register_config_tools(mcp) -> None:
    @mcp.tool
    def get_environments(
        db: Session = Depends(get_db_session),
    ) -> Dict[str, Any]:
        """Get the list of available environments (e.g. prod, staging, dev).

        The default environment is marked with is_default=True.

        Returns:
            List of environments with IDs, names, acronyms, and default status.
        """
        environments = EnvironmentService(db).get_environments()
        serialized = [
            EnvironmentGetItem.model_validate(e).model_dump() for e in environments
        ]
        default = next((e for e in environments if e.is_default), None)
        return {
            "environments": serialized,
            "count": len(serialized),
            "default_environment": EnvironmentGetItem.model_validate(
                default
            ).model_dump()
            if default
            else None,
        }

    @mcp.tool(
        description="""
    Get a high-level overview of the portal: total counts of data products, output ports,
    technical assets, a list of all domains with their IDs, and featured content.
    Use this as a starting point to orient the user, discover available domain IDs,
    or answer questions like 'what data is available?'.
    """
    )
    def get_marketplace_overview(
        db: Session = Depends(get_db_session),
        user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> dict[str, Any]:
        all_data_products = DataProductService(db).get_data_products(
            current_user=user, assignment_filter=AssignmentFilter.ALL
        )
        all_output_ports = OutputPortService(db).search_output_ports(
            query=None,
            limit=1000,
            user=user,
            assignment_filter=AssignmentFilter.ALL,
        )
        all_technical_assets = TechnicalAssetService(db).get_data_outputs()
        all_domains = DomainService(db).get_domains()

        popular_data_products = all_data_products[:5]
        popular_datasets = all_output_ports[:5]

        return {
            "statistics": {
                "total_data_products": len(all_data_products),
                "total_output_ports": len(all_output_ports),
                "total_technical_assets": len(all_technical_assets),
                "total_domains": len(all_domains),
            },
            "featured_content": {
                "popular_data_products": [
                    GetDataProductsResponseItem.model_validate(
                        GetDataProductsResponseItem.model_validate(dp)
                    ).model_dump()
                    for dp in popular_data_products
                ],
                "popular_output_ports": [
                    SearchOutputPortsResponseItem.model_validate(ds).model_dump()
                    for ds in popular_datasets
                ],
            },
            "domains": [
                GetDomainsItem.model_validate(domain).model_dump()
                for domain in all_domains
            ],
        }

    @mcp.tool(
        description="""
    Get analytics for a data product: its output ports and technical assets with counts.
    Use this to answer questions like 'what does this data product expose?' or 'how many datasets does it have?'.

    Args:
        data_product_id: UUID obtained from search_data_products or get_data_product_details.
    """
    )
    def get_data_product_analytics(
        data_product_id: str,
        db: Session = Depends(get_db_session),
        user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> dict[str, Any]:
        data_product = DataProductService(db).get_data_product(
            id=UUID(data_product_id),
        )

        if not data_product:
            return {"error": f"Data product {data_product_id} not found"}

        output_ports = OutputPortService(db).get_output_ports(
            user=user, data_product_id=UUID(data_product_id)
        )

        technical_assets = TechnicalAssetService(db).get_data_outputs()
        related_technical_assets = [
            do
            for do in technical_assets
            if hasattr(do, "data_product_id")
            and do.data_product_id == UUID(data_product_id)
        ]

        return {
            "data_product": GetDataProductResponse.model_validate(
                data_product
            ).model_dump(),
            "analytics": {
                "output_ports_count": len(output_ports),
                "technical_assets_count": len(related_technical_assets),
                "output_ports": [
                    OutputPort.model_validate(ds).model_dump() for ds in output_ports
                ],
                "technical_assets": [
                    GetTechnicalAssetsResponseItem.model_validate(do).model_dump()
                    for do in related_technical_assets
                ],
            },
        }
