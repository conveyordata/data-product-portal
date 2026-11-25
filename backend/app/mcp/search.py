"""Search and discovery tools for data products, output ports, domains, and technical assets."""

from typing import Annotated, Any, Optional, Sequence
from uuid import UUID

from fastmcp.dependencies import Depends
from pydantic import Field
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import AssignmentFilter
from app.configuration.domains.service import DomainService
from app.data_products.output_ports.input_ports.service import InputPortService
from app.data_products.output_ports.schema_response import GetOutputPortsResponseItem
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_response import GetDataProductsResponseItem
from app.data_products.service import DataProductService
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)
from app.data_products.technical_assets.service import TechnicalAssetService
from app.mcp.deps import get_mcp_authenticated_user, get_user_db_session
from app.search_data_products.schema_response import SearchDataProductsResponseItem
from app.users.model import User as UserModel


def universal_search(
    query: str,
    entity_types: Sequence[str] = (),
    limit: int = 10,
    db: Session = Depends(get_user_db_session),
    user: UserModel = Depends(get_mcp_authenticated_user),
) -> dict[str, Any]:
    results: dict[str, Any] = {
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
        all_data_products = DataProductService(db).get_data_products(
            assignment_filter=AssignmentFilter.ALL,
        )
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
        all_output_ports = OutputPortService(db).list_output_ports(
            user=user, assignment_filter=AssignmentFilter.ALL
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
            GetOutputPortsResponseItem.model_validate(op).model_dump()
            for op in filtered_output_ports
        ]
        query_results.update({"output_ports": result_datasets})
        total_count += len(filtered_output_ports)

    if "technical_assets" in search_types:
        all_technical_assets = TechnicalAssetService(db).get_technical_assets()
        filtered_technical_assets = []
        for do in all_technical_assets:
            if query.lower() in do.name.lower() or (
                do.description and query.lower() in do.description.lower()
            ):
                filtered_technical_assets.append(do)
                if len(filtered_technical_assets) >= limit:
                    break

        query_results.update(
            {
                "technical_assets": [
                    GetTechnicalAssetsResponseItem.model_validate(do)
                    for do in filtered_technical_assets
                ]
            }
        )
        total_count += len(filtered_technical_assets)

    if "domains" in search_types:
        from app.configuration.domains.schema_response import GetDomainsItem

        all_domains = DomainService(db).get_domains()
        filtered_domains = []
        for domain in all_domains:
            if query.lower() in domain.name.lower() or (
                domain.description and query.lower() in domain.description.lower()
            ):
                filtered_domains.append(domain)
                if len(filtered_domains) >= limit:
                    break

        result_domains = [
            GetDomainsItem.model_validate(domain).model_dump()
            for domain in filtered_domains
        ]
        query_results.update({"domains": result_domains})
        total_count += len(filtered_domains)
    results["total_count"] = total_count
    results["results"] = query_results
    return results


def search_data_products(
    query: Optional[str] = None,
    limit: Annotated[int, Field(ge=1, le=1000)] = 20,
    db: Session = Depends(get_user_db_session),
) -> dict[str, Any]:
    data_products = DataProductService(db).search_data_products(
        query=query, limit=limit
    )
    return {
        "data_products": [
            SearchDataProductsResponseItem.model_validate(dp).model_dump()
            for dp in data_products
        ],
        "count": len(data_products),
        "filters_applied": {"query": query},
    }


def get_consuming_products(
    output_port_id: str,
    data_product_id: str,
    db: Session = Depends(get_user_db_session),
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
    consuming_products = InputPortService(db).get_consuming_data_products(
        UUID(output_port_id), UUID(data_product_id)
    )
    return {
        "output_port_id": output_port_id,
        "consuming_data_products": [
            {
                "id": str(ip.consuming_abstract_data_product_id),
                "name": ip.consuming_abstract_data_product.name,
                "namespace": ip.consuming_abstract_data_product.namespace,
            }
            for ip in consuming_products
        ],
    }


def register_search_tools(mcp) -> None:
    mcp.tool(
        description="""
Search across data products, output ports, technical assets, and domains in a single call.
Use this only when the user hasn't specified what type of entity they're looking for.
For finding data, always prefer search_data_products — it uses semantic search and lists the output ports of each data product.
To get the data product details for output ports, you can use the get_data_product_details function with the data_product_id.
Args:
    query: Search query string
    entity_types: Filter to specific types. Valid values: 'data_products', 'output_ports',
                  'technical_assets', 'domains'. Leave empty to search all types.
    limit: Maximum number of results per entity type
"""
    )(universal_search)

    mcp.tool(
        description="""
    Search data products using semantic search. This is the preferred tool for finding data in the portal.
    Use this for any question about finding datasets, tables, or data sources.

    A data product is a container owned by a team, grouping related output ports and technical assets.
    An output port is a published, consumable dataset exposed by a data product.
    Each result lists the output ports of the data product, with their access modes.

    NEXT STEP: After finding a relevant output port, use get_output_port_details() to get the full details
    including data_product_links (consuming data products) which are essential for querying the data.
    To explore what a data product contains, follow up with get_data_product_details or get_data_product_analytics.

    Args:
        query: Natural language or keyword search. Results are ranked by relevance; leave empty to list data products by name.
        limit: Maximum number of results to return.
    """
    )(search_data_products)

    mcp.tool(get_consuming_products)
