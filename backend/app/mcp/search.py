"""Search and discovery tools for data products, output ports, domains, and technical assets."""

from typing import Any, Optional, Sequence
from uuid import UUID

from fastmcp.dependencies import Depends
from sqlalchemy.orm import Session

from app.configuration.domains.service import DomainService
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_response import GetDataProductsResponseItem
from app.data_products.service import DataProductService
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)
from app.data_products.technical_assets.service import DataOutputService
from app.mcp.deps import get_db_session, get_mcp_authenticated_user
from app.search_output_ports.schema_response import SearchOutputPortsResponseItem
from app.users.model import User as UserModel


def register_search_tools(mcp) -> None:
    @mcp.tool(
        description="""
Search across data products, output ports, technical assets, and domains in a single call.
Use this only when the user hasn't specified what type of entity they're looking for.
For output ports specifically, always prefer search_output_ports — it uses semantic search and returns richer metadata.
To get the data product details for output ports, you can use the get_data_product_details function with the data_product_id.
Args:
    query: Search query string
    entity_types: Filter to specific types. Valid values: 'data_products', 'output_ports',
                  'technical_assets', 'domains'. Leave empty to search all types.
    limit: Maximum number of results per entity type
"""
    )
    def universal_search(
        query: str,
        entity_types: Sequence[str] = (),
        limit: int = 10,
        db: Session = Depends(get_db_session),
        user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> dict[str, Any]:
        results = {
            "query": query,
            "results": {},
            "total_count": 0,
        }
        total_count = 0
        search_types = entity_types or [
            "data_products",
            "output_ports",
            "technical_assets",
            "domains",
        ]
        query_results = {}
        if "data_products" in search_types:
            all_data_products = DataProductService(db).get_data_products()
            filtered_data_products = []
            for dp in all_data_products:
                if query.lower() in dp.name.lower() or (
                    dp.description and query.lower() in dp.description.lower()
                ):
                    filtered_data_products.append(
                        GetDataProductsResponseItem.model_validate(dp)
                    )
                    if len(filtered_data_products) >= limit:
                        break

            result_data_products = [
                GetDataProductsResponseItem.model_validate(dp).model_dump()
                for dp in filtered_data_products
            ]
            query_results.update({"data_products": result_data_products})
            total_count += len(filtered_data_products)

        if "output_ports" in search_types:
            all_output_ports = OutputPortService(db).search_output_ports(
                query=None, limit=1000, user=user, current_user_assigned=False
            )
            filtered_output_ports = []
            for ds in all_output_ports:
                if query.lower() in ds.name.lower() or (
                    ds.description and query.lower() in ds.description.lower()
                ):
                    filtered_output_ports.append(ds)
                    if len(filtered_output_ports) >= limit:
                        break

            result_datasets = [
                SearchOutputPortsResponseItem.model_validate(op).model_dump()
                for op in filtered_output_ports
            ]
            query_results.update({"output_ports": result_datasets})
            total_count += len(filtered_output_ports)

        if "technical_assets" in search_types:
            all_data_outputs = DataOutputService(db).get_data_outputs()
            filtered_data_outputs = []
            for do in all_data_outputs:
                if query.lower() in do.name.lower() or (
                    do.description and query.lower() in do.description.lower()
                ):
                    filtered_data_outputs.append(do)
                    if len(filtered_data_outputs) >= limit:
                        break

            result_data_outputs = [
                GetTechnicalAssetsResponseItem.model_validate(do)
                for do in filtered_data_outputs
            ]
            query_results.update({"technical_assets": result_data_outputs})
            total_count += len(filtered_data_outputs)

        if "domains" in search_types:
            all_domains = DomainService(db).get_domains()
            filtered_domains = []
            for domain in all_domains:
                if query.lower() in domain.name.lower() or (
                    domain.description and query.lower() in domain.description.lower()
                ):
                    filtered_domains.append(domain)
                    if len(filtered_domains) >= limit:
                        break

            from app.configuration.domains.schema_response import GetDomainsItem

            result_domains = [
                GetDomainsItem.model_validate(domain).model_dump()
                for domain in filtered_domains
            ]
            query_results.update({"domains": result_domains})
            total_count += len(filtered_domains)
        results["total_count"] = total_count
        results["results"] = query_results
        return results

    @mcp.tool(
        description="""
    Search and filter data products. Only use this when the user explicitly asks to find a data product.
    For general data discovery, prefer search_output_ports instead.

    A data product is a container owned by a team, grouping related output ports and technical assets.
    To explore what a data product contains, follow up with get_data_product_details or get_data_product_analytics.

    Args:
        query: Keyword search on name and description. Leave empty to list all data products.
        domain_id: UUID of the domain to filter by — use get_marketplace_overview to list available domains.
        status: Lifecycle state. Common values: 'active', 'pending', 'archived'.
        limit: Maximum number of results to return.
    """
    )
    def search_data_products(
        query: Optional[str] = None,
        domain_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        db: Session = Depends(get_db_session),
    ) -> dict[str, Any]:
        all_data_products = DataProductService(db).get_data_products()
        filtered_data_products = []

        for dp in all_data_products:
            if (
                query
                and query.lower() not in dp.name.lower()
                and (not dp.description or query.lower() not in dp.description.lower())
            ):
                continue
            if domain_id and str(dp.domain_id) != domain_id:
                continue
            if status and dp.status != status:
                continue

            filtered_data_products.append(
                GetDataProductsResponseItem.model_validate(dp)
            )
            if len(filtered_data_products) >= limit:
                break
        return {
            "data_products": [
                GetDataProductsResponseItem.model_validate(dp).model_dump()
                for dp in filtered_data_products
            ],
            "count": len(filtered_data_products),
            "filters_applied": {
                "query": query,
                "domain_id": domain_id,
                "status": status,
            },
        }

    @mcp.tool
    def get_consuming_products(
        output_port_id: str,
        data_product_id: str,
        db: Session = Depends(get_db_session),
        user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> dict[str, Any]:
        """Get consuming data products for a specific output port.

        Essential for understanding who has access to the data and how users
        typically access it.

        Args:
            output_port_id: UUID of the output port (dataset) to check.
            data_product_id: UUID of the owning data product of the output port.
        Returns:
            List of consuming data products with their namespaces and descriptions.
        """
        consuming_products = OutputPortService(db).get_consuming_data_products(
            UUID(output_port_id), UUID(data_product_id)
        )
        return {
            "output_port_id": output_port_id,
            "consuming_data_products": [
                {
                    "id": str(ip.consuming_abstract_data_product.id),
                    "name": ip.consuming_abstract_data_product.name,
                    "namespace": ip.consuming_abstract_data_product.namespace,
                    "description": ip.consuming_abstract_data_product.description,
                }
                for ip in consuming_products
            ],
        }

    @mcp.tool(
        description="""
    Search output ports (datasets) using semantic search. This is the preferred tool for finding data in the portal.
    Use this for any question about finding datasets, tables, or data sources — unless the user explicitly asks for a data product.

    An output port is a published, consumable dataset exposed by a data product.
    Returns the name, description, access type, owner, and parent data product for each result.

    NEXT STEP: After finding relevant output ports, use get_output_port_details() to get the full details
    including data_product_links (consuming data products) which are essential for querying the data.

    Args:
        query: Natural language or keyword search. Leave empty to list all accessible output ports.
        limit: Maximum number of results to return.
    """
    )
    def search_output_ports(
        query: Optional[str] = None,
        limit: int = 20,
        db: Session = Depends(get_db_session),
        user: UserModel = Depends(get_mcp_authenticated_user),
    ) -> dict[str, Any]:
        all_output_ports = OutputPortService(db).search_output_ports(
            query=query, user=user, limit=limit, current_user_assigned=False
        )
        return {
            "output_ports": [
                SearchOutputPortsResponseItem.model_validate(ds).model_dump()
                for ds in all_output_ports
            ],
            "count": len(all_output_ports),
            "filters_applied": {
                "query": query,
            },
        }
