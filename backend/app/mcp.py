from typing import Any, Dict, List, Optional
from uuid import UUID

from fastmcp import FastMCP
from sqlalchemy.orm import configure_mappers

from app.core.auth.jwt import JWTToken

# Import Pydantic schemas - corrected paths
from app.data_outputs.schema_response import DataOutputGet, DataOutputsGet

# Import existing services
from app.data_outputs.service import DataOutputService

# Import enums - corrected paths
from app.data_products.schema_response import DataProductGet, DataProductsGet
from app.data_products.service import DataProductService
from app.database.database import get_db_session
from app.datasets.schema_response import DatasetGet, DatasetsGet
from app.datasets.service import DatasetService
from app.domains.schema_response import DomainGet
from app.domains.service import DomainService


def initialize_models():
    """Initialize all SQLAlchemy models and resolve relationships"""
    try:
        configure_mappers()
    except Exception as e:
        print(f"Warning during model initialization: {e}")


initialize_models()

mcp = FastMCP("DataProductPortalMCPServer")

# ==============================================================================
# CORE DISCOVERY & SEARCH TOOLS
# ==============================================================================


def get_current_user():
    from app.core.auth.auth import get_authenticated_user

    user = get_authenticated_user(
        token=JWTToken(sub="systemaccount_bot", token=""), db=next(get_db_session())
    )
    return user


@mcp.tool
def universal_search(
    query: str, entity_types: Optional[List[str]] = None, limit: int = 10
) -> Dict[str, Any]:
    """
    Universal search across data products, datasets, and data outputs.

    Args:
        query: Search query string
        entity_types: List of entity types to search (data_products, datasets, data_outputs, domains)
        limit: Maximum number of results per entity type
    """
    try:
        db = next(get_db_session())
        user = get_current_user()
        try:
            results = {"query": query, "results": {}, "total_count": 0}

            search_types = entity_types or [
                "data_products",
                "datasets",
                "data_outputs",
                "domains",
            ]

            # Search Data Products - get all and filter manually
            if "data_products" in search_types:
                all_data_products = DataProductService(db).get_data_products()
                # Filter by query manually
                filtered_data_products = []
                for dp in all_data_products:
                    if query.lower() in dp.name.lower() or (
                        dp.description and query.lower() in dp.description.lower()
                    ):
                        filtered_data_products.append(dp)
                        if len(filtered_data_products) >= limit:
                            break

                results["results"]["data_products"] = [
                    DataProductsGet.model_validate(dp).model_dump()
                    for dp in filtered_data_products
                ]
                results["total_count"] += len(filtered_data_products)

            # Search Datasets - get all and filter manually
            if "datasets" in search_types:
                all_datasets = DatasetService(db).get_datasets(user=user)
                # Filter by query manually
                filtered_datasets = []
                for ds in all_datasets:
                    if query.lower() in ds.name.lower() or (
                        ds.description and query.lower() in ds.description.lower()
                    ):
                        filtered_datasets.append(ds)
                        if len(filtered_datasets) >= limit:
                            break

                results["results"]["datasets"] = [
                    DatasetsGet.model_validate(ds).model_dump()
                    for ds in filtered_datasets
                ]
                results["total_count"] += len(filtered_datasets)

            # Search Data Outputs - get all and filter manually
            if "data_outputs" in search_types:
                all_data_outputs = DataOutputService(db).get_data_outputs()
                # Filter by query manually
                filtered_data_outputs = []
                for do in all_data_outputs:
                    if query.lower() in do.name.lower() or (
                        do.description and query.lower() in do.description.lower()
                    ):
                        filtered_data_outputs.append(do)
                        if len(filtered_data_outputs) >= limit:
                            break

                results["results"]["data_outputs"] = [
                    DataOutputsGet.model_validate(do).model_dump()
                    for do in filtered_data_outputs
                ]
                results["total_count"] += len(filtered_data_outputs)

            # Search Domains - get all and filter manually
            if "domains" in search_types:
                all_domains = DomainService(db).get_domains()
                # Filter by query manually
                filtered_domains = []
                for domain in all_domains:
                    if query.lower() in domain.name.lower() or (
                        domain.description
                        and query.lower() in domain.description.lower()
                    ):
                        filtered_domains.append(domain)
                        if len(filtered_domains) >= limit:
                            break

                results["results"]["domains"] = [
                    DomainGet.model_validate(domain).model_dump()
                    for domain in filtered_domains
                ]
                results["total_count"] += len(filtered_domains)

            return results
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


@mcp.tool
def search_data_products(
    query: Optional[str] = None,
    domain_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Search data products with filters using the existing service layer."""
    try:
        db = next(get_db_session())
        try:
            # Get all data products and filter manually
            all_data_products = DataProductService(db).get_data_products()
            filtered_data_products = []

            for dp in all_data_products:
                # Apply filters manually
                if (
                    query
                    and query.lower() not in dp.name.lower()
                    and (
                        not dp.description
                        or query.lower() not in dp.description.lower()
                    )
                ):
                    continue
                if domain_id and str(dp.domain_id) != domain_id:
                    continue
                if status and str(dp.status) != status:
                    continue

                filtered_data_products.append(dp)
                if len(filtered_data_products) >= limit:
                    break

            return {
                "data_products": [
                    DataProductsGet.model_validate(dp).model_dump()
                    for dp in filtered_data_products
                ],
                "count": len(filtered_data_products),
                "filters_applied": {
                    "query": query,
                    "domain_id": domain_id,
                    "status": status,
                },
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to search data products: {str(e)}"}


@mcp.tool
def search_datasets(
    query: Optional[str] = None,
    access_type: Optional[str] = None,
    domain_id: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """Search datasets with filters using the existing service layer."""
    try:
        db = next(get_db_session())
        user = get_current_user()
        try:
            # Get all datasets and filter manually
            all_datasets = DatasetService(db).get_datasets(user=user)
            filtered_datasets = []

            for ds in all_datasets:
                # Apply filters manually
                if (
                    query
                    and query.lower() not in ds.name.lower()
                    and (
                        not ds.description
                        or query.lower() not in ds.description.lower()
                    )
                ):
                    continue
                if access_type and str(ds.access_type) != access_type:
                    continue
                if (
                    domain_id
                    and hasattr(ds, "domain_id")
                    and str(ds.domain_id) != domain_id
                ):
                    continue

                filtered_datasets.append(ds)
                if len(filtered_datasets) >= limit:
                    break

            return {
                "datasets": [
                    DatasetsGet.model_validate(ds).model_dump()
                    for ds in filtered_datasets
                ],
                "count": len(filtered_datasets),
                "filters_applied": {
                    "query": query,
                    "access_type": access_type,
                    "domain_id": domain_id,
                },
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to search datasets: {str(e)}"}


# ==============================================================================
# DETAILED ENTITY INFORMATION
# ==============================================================================


@mcp.tool
def get_data_product_details(data_product_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific data product."""
    try:
        db = next(get_db_session())
        try:
            data_product = DataProductService(db).get_data_product(
                id=UUID(data_product_id),
            )

            if not data_product:
                return {"error": f"Data product {data_product_id} not found"}

            # Use Pydantic schema for serialization
            return DataProductGet.model_validate(data_product).model_dump()
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data product details: {str(e)}"}


@mcp.tool
def get_dataset_details(dataset_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific dataset."""
    try:
        db = next(get_db_session())
        user = get_current_user()
        try:
            dataset = DatasetService(db).get_dataset(id=UUID(dataset_id), user=user)

            if not dataset:
                return {"error": f"Dataset {dataset_id} not found"}

            return DatasetGet.model_validate(dataset).model_dump()
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get dataset details: {str(e)}"}


@mcp.tool
def get_data_output_details(data_output_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific data output."""
    try:
        db = next(get_db_session())
        try:
            data_output = DataOutputService(db).get_data_output(
                id=UUID(data_output_id),
            )

            if not data_output:
                return {"error": f"Data output {data_output_id} not found"}

            return DataOutputGet.model_validate(data_output).model_dump()
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data output details: {str(e)}"}


@mcp.tool
def get_domain_details(domain_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific domain."""
    try:
        db = next(get_db_session())
        try:
            domain = DomainService(db).get_domain(
                id=UUID(domain_id),
            )

            if not domain:
                return {"error": f"Domain {domain_id} not found"}

            return DomainGet.model_validate(domain).model_dump()
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get domain details: {str(e)}"}


# ==============================================================================
# MARKETPLACE & ANALYTICS
# ==============================================================================


@mcp.tool
def get_marketplace_overview() -> Dict[str, Any]:
    """Get marketplace overview with statistics and featured content."""
    try:
        db = next(get_db_session())
        user = get_current_user()
        try:
            # Get counts by querying all and taking length
            all_data_products = DataProductService(db).get_data_products()
            all_datasets = DatasetService(db).get_datasets(user=user)
            all_data_outputs = DataOutputService(db).get_data_outputs()
            all_domains = DomainService(db).get_domains()

            # Get first 5 items as "popular" (since we can't sort)
            popular_data_products = all_data_products[:5]
            popular_datasets = all_datasets[:5]

            return {
                "statistics": {
                    "total_data_products": len(all_data_products),
                    "total_datasets": len(all_datasets),
                    "total_data_outputs": len(all_data_outputs),
                    "total_domains": len(all_domains),
                },
                "featured_content": {
                    "popular_data_products": [
                        DataProductsGet.model_validate(dp).model_dump()
                        for dp in popular_data_products
                    ],
                    "popular_datasets": [
                        DatasetsGet.model_validate(ds).model_dump()
                        for ds in popular_datasets
                    ],
                },
                "domains": [
                    DomainGet.model_validate(domain).model_dump()
                    for domain in all_domains
                ],
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get marketplace overview: {str(e)}"}


@mcp.tool
def get_data_product_analytics(data_product_id: str) -> Dict[str, Any]:
    """Get analytics and usage statistics for a data product."""
    try:
        db = next(get_db_session())
        user = get_current_user()
        try:
            # Get the data product using service
            data_product = DataProductService(db).get_data_product(
                id=UUID(data_product_id),
            )

            if not data_product:
                return {"error": f"Data product {data_product_id} not found"}

            # Get related datasets - filter manually from all datasets
            all_datasets = DatasetService(db).get_datasets(user=user)
            related_datasets = [
                ds
                for ds in all_datasets
                if hasattr(ds, "data_product_id")
                and ds.data_product_id == UUID(data_product_id)
            ]

            # Get related data outputs - filter manually from all data outputs
            all_data_outputs = DataOutputService(db).get_data_outputs()
            related_data_outputs = [
                do
                for do in all_data_outputs
                if hasattr(do, "data_product_id")
                and do.data_product_id == UUID(data_product_id)
            ]

            return {
                "data_product": DataProductsGet.model_validate(
                    data_product
                ).model_dump(),
                "analytics": {
                    "datasets_count": len(related_datasets),
                    "data_outputs_count": len(related_data_outputs),
                    "datasets": [
                        DatasetsGet.model_validate(ds).model_dump()
                        for ds in related_datasets
                    ],
                    "data_outputs": [
                        DataOutputsGet.model_validate(do).model_dump()
                        for do in related_data_outputs
                    ],
                },
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data product analytics: {str(e)}"}


# ==============================================================================
# RESOURCE ENDPOINTS
# ==============================================================================


@mcp.resource("data-product://{data_product_id}")
def get_data_product_resource(data_product_id: str) -> str:
    """Get data product as a resource."""
    try:
        db = next(get_db_session())
        try:
            data_product = DataProductService(db).get_data_product(
                id=UUID(data_product_id),
            )

            if not data_product:
                return f"Error: Data product {data_product_id} not found"

            # Convert to Pydantic model and then to formatted string
            dp_data = DataProductGet.model_validate(data_product)

            return f"""
# Data Product: {dp_data.name}

**ID:** {dp_data.id}
**Status:** {dp_data.status}
**Domain:** {dp_data.domain.name if dp_data.domain else 'N/A'}
**Description:** {dp_data.description or 'No description available'}

## Metadata
- **Created:** {dp_data.created_at}
- **Updated:** {dp_data.updated_at}
- **Owner:** {dp_data.owner_email or 'N/A'}

## Datasets
{len(dp_data.datasets) if dp_data.datasets else 0} dataset(s) associated

## Data Outputs
{len(dp_data.data_outputs) if dp_data.data_outputs else 0} data output(s) associated
"""
        finally:
            db.close()

    except Exception as e:
        return f"Error retrieving data product resource: {str(e)}"


@mcp.resource("dataset://{dataset_id}")
def get_dataset_resource(dataset_id: str) -> str:
    """Get dataset as a resource."""
    try:
        db = next(get_db_session())
        user = get_current_user()
        try:
            dataset = DatasetService(db).get_dataset(id=UUID(dataset_id), user=user)

            if not dataset:
                return f"Error: Dataset {dataset_id} not found"
            # Convert to Pydantic model and then to formatted string
            ds_data = DatasetGet.model_validate(dataset)

            return f"""
# Dataset: {ds_data.name}

**ID:** {ds_data.id}
**Status:** {ds_data.status}
**Description:** {ds_data.description or 'No description available'}

## Metadata
- **Created:** {ds_data.created_at}
- **Updated:** {ds_data.updated_at}
- **Owner:** {ds_data.owner_email or 'N/A'}

## Data Product
**ID:** {ds_data.data_product_id}
**Name:** {ds_data.data_product_name}
"""
        finally:
            db.close()

    except Exception as e:
        return f"Error retrieving dataset resource: {str(e)}"


@mcp.resource("marketplace://overview")
def get_marketplace_resource() -> str:
    """Get marketplace overview as a resource."""
    try:
        overview = get_marketplace_overview()

        if "error" in overview:
            return f"Error: {overview['error']}"

        stats = overview["statistics"]

        return f"""
# Data Product Portal - Marketplace Overview

## Statistics
- **Data Products:** {stats['total_data_products']}
- **Datasets:** {stats['total_datasets']}
- **Data Outputs:** {stats['total_data_outputs']}
- **Domains:** {stats['total_domains']}

## Popular Data Products
{chr(10).join([f"- {dp['name']} ({dp['status']})" for dp in overview['featured_content']['popular_data_products']])}

## Popular Datasets
{chr(10).join([f"- {ds['name']} ({ds.get('access_type', 'N/A')})" for ds in overview['featured_content']['popular_datasets']])}

## Available Domains
{chr(10).join([f"- {domain['name']}: {domain['description'] or 'No description'}" for domain in overview['domains']])}
"""

    except Exception as e:
        return f"Error retrieving marketplace overview: {str(e)}"
