import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastmcp import FastMCP
from sqlalchemy.orm import configure_mappers, joinedload, raiseload

from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_products.model import DataProduct as DataProductModel
from app.data_products_datasets.model import DataProductDatasetAssociation

# from app.database.database import get_db_session
from app.datasets.enums import DatasetAccessType
from app.datasets.model import Dataset as DatasetModel
from app.domains.model import Domain as DomainModel

# Import utilities and models
from app.mcp_utils import MCP_CONFIG, DataPortalMCPUtils, EntityNotFoundError
from app.platforms.model import Platform as PlatformModel
from app.role_assignments.enums import DecisionStatus


# Add this before any database operations
def initialize_models():
    """Initialize all SQLAlchemy models and resolve relationships"""
    try:
        # Import all models to ensure they're registered
        # from app.data_product_types.model import DataProductType
        # from app.role_assignments.data_product.model import DataProductRoleAssignment
        # from app.roles.model import Role

        # ... import other models
        # Force relationship resolution
        configure_mappers()
    except Exception as e:
        print(f"Warning during model initialization: {e}")


# Call this at module level
initialize_models()

mcp = FastMCP("DataProductPortalMCPServer")

# ==============================================================================
# CORE DISCOVERY & SEARCH TOOLS
# ==============================================================================


@mcp.tool
def universal_search(
    query: str,
    search_data_products: bool = True,
    search_datasets: bool = True,
    search_data_outputs: bool = True,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Universal search across all data portal entities (data products, datasets, data outputs).

    Args:
        query: Search query string
        search_data_products: Whether to search data products
        search_datasets: Whether to search datasets
        search_data_outputs: Whether to search data outputs
        limit: Maximum results per entity type
    """
    try:
        # Convert boolean flags to entity_types list for the utility function
        entity_types = []
        if search_data_products:
            entity_types.append("data_products")
        if search_datasets:
            entity_types.append("datasets")
        if search_data_outputs:
            entity_types.append("data_outputs")

        return DataPortalMCPUtils.search_across_entities(
            query, entity_types if entity_types else None, limit
        )
    except EntityNotFoundError as e:
        return {"error": f"Entity not found: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@mcp.tool
def search_data_products(
    name_filter: Optional[str] = None,
    domain_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Search and discover data products in the marketplace.

    Args:
        name_filter: Filter by data product name (partial match)
        domain_filter: Filter by domain name
        status_filter: Filter by status (active, inactive, etc.)
        limit: Maximum number of results to return
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import select

        query = (
            select(DataProductModel)
            .options(
                joinedload(DataProductModel.dataset_links).raiseload("*"),
                joinedload(DataProductModel.assignments).raiseload("*"),
                joinedload(DataProductModel.data_outputs).raiseload("*"),
            )
            .join(DomainModel)
        )

        if name_filter:
            query = query.where(DataProductModel.name.ilike(f"%{name_filter}%"))

        if domain_filter:
            query = query.where(DomainModel.name.ilike(f"%{domain_filter}%"))

        if status_filter:
            query = query.where(DataProductModel.status == status_filter)

        query = query.limit(limit)

        data_products = db.scalars(query).unique().all()

        return [
            DataPortalMCPUtils.format_entity_summary(dp, "data_product")
            for dp in data_products
        ]
    except Exception as e:
        return [{"error": f"Error searching data products: {str(e)}"}]
    finally:
        db.close()


@mcp.tool
def search_datasets(
    name_filter: Optional[str] = None,
    domain_filter: Optional[str] = None,
    access_type_filter: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Search and discover datasets in the marketplace.

    Args:
        name_filter: Filter by dataset name (partial match)
        domain_filter: Filter by domain name
        access_type_filter: Filter by access type (public, private, etc.)
        limit: Maximum number of results to return
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import select

        query = (
            select(DatasetModel)
            .options(
                joinedload(DatasetModel.data_product_links)
                .joinedload(DataProductDatasetAssociation.data_product)
                .raiseload("*"),
                joinedload(DatasetModel.data_output_links)
                .joinedload(DataOutputDatasetAssociation.data_output)
                .options(
                    joinedload(DataOutputModel.configuration),
                    joinedload(DataOutputModel.owner),
                    raiseload("*"),
                ),
            )
            .join(DomainModel)
        )

        if name_filter:
            query = query.where(DatasetModel.name.ilike(f"%{name_filter}%"))

        if domain_filter:
            query = query.where(DomainModel.name.ilike(f"%{domain_filter}%"))

        if access_type_filter:
            query = query.where(DatasetModel.access_type == access_type_filter)

        query = query.limit(limit)

        datasets = db.scalars(query).unique().all()

        return [
            DataPortalMCPUtils.format_entity_summary(ds, "dataset") for ds in datasets
        ]
    finally:
        db.close()


# ==============================================================================
# DETAILED ENTITY INFORMATION
# ==============================================================================


@mcp.tool
def get_data_product_details(data_product_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific data product.

    Args:
        data_product_id: UUID of the data product
    """
    db = DataPortalMCPUtils.get_db()

    try:
        dp = db.get(DataProductModel, UUID(data_product_id))
        if not dp:
            raise EntityNotFoundError(f"Data product {data_product_id} not found")

        result = {
            "id": str(dp.id),
            "name": dp.name,
            "namespace": dp.namespace,
            "description": dp.description,
            "about": dp.about,
            "status": dp.status.value if dp.status else None,
            "domain": (
                {
                    "id": str(dp.domain.id),
                    "name": dp.domain.name,
                    "description": dp.domain.description,
                }
                if dp.domain
                else None
            ),
            "type": (
                {
                    "id": str(dp.type.id),
                    "name": dp.type.name,
                    "description": dp.type.description,
                }
                if dp.type
                else None
            ),
            "lifecycle": (
                {
                    "id": str(dp.lifecycle.id),
                    "name": dp.lifecycle.name,
                    "value": dp.lifecycle.value,
                }
                if dp.lifecycle
                else None
            ),
            "tags": [{"id": str(tag.id), "name": tag.name} for tag in dp.tags],
            "metrics": {
                "user_count": dp.user_count,
                "dataset_count": dp.dataset_count,
                "data_outputs_count": dp.data_outputs_count,
            },
            "created_on": dp.created_on.isoformat() if dp.created_on else None,
            "updated_on": dp.updated_on.isoformat() if dp.updated_on else None,
        }

        return result
    finally:
        db.close()


@mcp.tool
def get_dataset_details(dataset_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific dataset.

    Args:
        dataset_id: UUID of the dataset
    """
    db = DataPortalMCPUtils.get_db()

    try:
        ds = db.get(DatasetModel, UUID(dataset_id))
        if not ds:
            raise EntityNotFoundError(f"Dataset {dataset_id} not found")

        result = {
            "id": str(ds.id),
            "name": ds.name,
            "namespace": ds.namespace,
            "description": ds.description,
            "about": ds.about,
            "status": ds.status.value if ds.status else None,
            "access_type": ds.access_type.value if ds.access_type else None,
            "domain": (
                {
                    "id": str(ds.domain.id),
                    "name": ds.domain.name,
                    "description": ds.domain.description,
                }
                if ds.domain
                else None
            ),
            "lifecycle": (
                {
                    "id": str(ds.lifecycle.id),
                    "name": ds.lifecycle.name,
                    "value": ds.lifecycle.value,
                }
                if ds.lifecycle
                else None
            ),
            "tags": [{"id": str(tag.id), "name": tag.name} for tag in ds.tags],
            "metrics": {"data_product_count": ds.data_product_count},
            "created_on": ds.created_on.isoformat() if ds.created_on else None,
            "updated_on": ds.updated_on.isoformat() if ds.updated_on else None,
        }

        return result
    finally:
        db.close()


@mcp.tool
def get_data_product_outputs(data_product_id: str) -> List[Dict[str, Any]]:
    """
    Get all data outputs for a specific data product.

    Args:
        data_product_id: UUID of the data product
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import select

        outputs = db.scalars(
            select(DataOutputModel).where(
                DataOutputModel.owner_id == UUID(data_product_id)
            )
        ).all()

        results = []
        for output in outputs:
            result = DataPortalMCPUtils.format_entity_summary(output, "data_output")
            result.update(
                {
                    "configuration": (
                        output.configuration.model_dump()
                        if output.configuration
                        else None
                    ),
                    "result_string": getattr(output, "result_string", None),
                    "technical_info": getattr(output, "technical_info", []),
                }
            )
            results.append(result)

        return results
    finally:
        db.close()


@mcp.tool
def get_dataset_data_outputs(dataset_id: str) -> List[Dict[str, Any]]:
    """
    Get all data outputs linked to a specific dataset.

    Args:
        dataset_id: UUID of the dataset
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import select

        # Get data outputs linked to this dataset
        links = (
            db.scalars(
                select(DataOutputDatasetAssociation)
                .where(DataOutputDatasetAssociation.dataset_id == UUID(dataset_id))
                .where(DataOutputDatasetAssociation.status == DecisionStatus.APPROVED)
            )
            .unique()
            .all()
        )

        results = []
        for link in links:
            output = link.data_output
            result = DataPortalMCPUtils.format_entity_summary(output, "data_output")
            result.update(
                {
                    "owner": {
                        "id": str(output.owner.id),
                        "name": output.owner.name,
                        "namespace": output.owner.namespace,
                    },
                    "configuration": (
                        output.configuration.model_dump()
                        if output.configuration
                        else None
                    ),
                    "linked_on": (
                        link.approved_on.isoformat() if link.approved_on else None
                    ),
                    "link_status": link.status.value,
                }
            )
            results.append(result)

        return results
    finally:
        db.close()


# ==============================================================================
# MARKETPLACE & ANALYTICS
# ==============================================================================


@mcp.tool
def get_marketplace_overview() -> Dict[str, Any]:
    """
    Get an overview of the data marketplace including counts and recent activity.
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import func, select

        # Get counts
        data_product_count = db.scalar(select(func.count(DataProductModel.id)))
        dataset_count = db.scalar(select(func.count(DatasetModel.id)))
        data_output_count = db.scalar(select(func.count(DataOutputModel.id)))
        domain_count = db.scalar(select(func.count(DomainModel.id)))

        # Get top domains by data product count
        top_domains = (
            db.execute(
                select(
                    DomainModel.name,
                    DomainModel.description,
                    func.count(DataProductModel.id).label("product_count"),
                )
                .join(DataProductModel)
                .group_by(DomainModel.id, DomainModel.name, DomainModel.description)
                .order_by(func.count(DataProductModel.id).desc())
                .limit(5)
            )
            .unique()
            .all()
        )

        # Get recent data products
        recent_products = (
            db.scalars(
                select(DataProductModel)
                .order_by(DataProductModel.created_on.desc())
                .limit(5)
            )
            .unique()
            .all()
        )

        # Get public datasets
        public_datasets = (
            db.scalars(
                select(DatasetModel)
                .where(DatasetModel.access_type == DatasetAccessType.PUBLIC)
                .order_by(DatasetModel.created_on.desc())
                .limit(5)
            )
            .unique()
            .all()
        )

        result = {
            "overview": {
                "total_data_products": data_product_count,
                "total_datasets": dataset_count,
                "total_data_outputs": data_output_count,
                "total_domains": domain_count,
            },
            "top_domains": [
                {
                    "name": domain.name,
                    "description": domain.description,
                    "data_product_count": domain.product_count,
                }
                for domain in top_domains
            ],
            "recent_data_products": [
                DataPortalMCPUtils.format_entity_summary(dp, "data_product")
                for dp in recent_products
            ],
            "public_datasets": [
                DataPortalMCPUtils.format_entity_summary(ds, "dataset")
                for ds in public_datasets
            ],
        }

        return result
    finally:
        db.close()


@mcp.tool
def get_trending_data(days: int = 7) -> Dict[str, Any]:
    """
    Get trending datasets and active data products based on recent activity.

    Args:
        days: Number of days to look back for trending analysis
    """
    return DataPortalMCPUtils.get_trending_data(days)


@mcp.tool
def get_activity_feed(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get recent activity feed across the data portal.

    Args:
        limit: Maximum number of activities to return
    """
    return DataPortalMCPUtils.get_activity_feed(limit)


@mcp.tool
def get_user_recommendations(user_id: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get personalized recommendations for a user based on their activity and interests.

    Args:
        user_id: UUID of the user
        limit: Maximum number of recommendations
    """
    return DataPortalMCPUtils.get_user_recommendations(user_id, limit)


# ==============================================================================
# DATA LINEAGE & RELATIONSHIPS
# ==============================================================================


@mcp.tool
def get_data_lineage(entity_id: str, entity_type: str) -> Dict[str, Any]:
    """
    Get data lineage for a data product, dataset, or data output.

    Args:
        entity_id: UUID of the entity
        entity_type: Type of entity (data_product, dataset, data_output)
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import select

        lineage = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "upstream": [],
            "downstream": [],
        }

        if entity_type == "data_product":
            # Get upstream datasets (datasets this data product consumes)
            upstream_links = (
                db.scalars(
                    select(DataProductDatasetAssociation)
                    .where(
                        DataProductDatasetAssociation.data_product_id == UUID(entity_id)
                    )
                    .where(
                        DataProductDatasetAssociation.status == DecisionStatus.APPROVED
                    )
                )
                .unique()
                .all()
            )

            for link in upstream_links:
                dataset = link.dataset
                lineage["upstream"].append(
                    {
                        "id": str(dataset.id),
                        "name": dataset.name,
                        "namespace": dataset.namespace,
                        "type": "dataset",
                        "relationship": "consumes",
                        "approved_on": (
                            link.approved_on.isoformat() if link.approved_on else None
                        ),
                    }
                )

            # Get downstream (data outputs this data product produces)
            data_outputs = (
                db.scalars(
                    select(DataOutputModel).where(
                        DataOutputModel.owner_id == UUID(entity_id)
                    )
                )
                .unique()
                .all()
            )

            for output in data_outputs:
                lineage["downstream"].append(
                    {
                        "id": str(output.id),
                        "name": output.name,
                        "namespace": output.namespace,
                        "type": "data_output",
                        "relationship": "produces",
                        "status": output.status.value if output.status else None,
                    }
                )

        elif entity_type == "dataset":
            # Get data outputs linked to this dataset
            output_links = (
                db.scalars(
                    select(DataOutputDatasetAssociation)
                    .where(DataOutputDatasetAssociation.dataset_id == UUID(entity_id))
                    .where(
                        DataOutputDatasetAssociation.status == DecisionStatus.APPROVED
                    )
                )
                .unique()
                .all()
            )

            for link in output_links:
                output = link.data_output
                lineage["upstream"].append(
                    {
                        "id": str(output.id),
                        "name": output.name,
                        "namespace": output.namespace,
                        "type": "data_output",
                        "owner": output.owner.name,
                        "relationship": "sourced_from",
                        "approved_on": (
                            link.approved_on.isoformat() if link.approved_on else None
                        ),
                    }
                )

            # Get data products that consume this dataset
            consuming_links = (
                db.scalars(
                    select(DataProductDatasetAssociation)
                    .where(DataProductDatasetAssociation.dataset_id == UUID(entity_id))
                    .where(
                        DataProductDatasetAssociation.status == DecisionStatus.APPROVED
                    )
                )
                .unique()
                .all()
            )

            for link in consuming_links:
                data_product = link.data_product
                lineage["downstream"].append(
                    {
                        "id": str(data_product.id),
                        "name": data_product.name,
                        "namespace": data_product.namespace,
                        "type": "data_product",
                        "relationship": "consumed_by",
                        "approved_on": (
                            link.approved_on.isoformat() if link.approved_on else None
                        ),
                    }
                )

        return lineage
    finally:
        db.close()


# ==============================================================================
# ACCESS & PERMISSIONS
# ==============================================================================


@mcp.tool
def check_dataset_access(user_id: str, dataset_id: str) -> Dict[str, Any]:
    """
    Check if a user has access to a specific dataset through their data product assignments.

    Args:
        user_id: UUID of the user
        dataset_id: UUID of the dataset
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import and_, select

        # Get user's approved data product assignments
        user_data_products = (
            db.scalars(
                select(DataProductModel)
                .join(DataProductModel.assignments)
                .where(
                    and_(
                        DataProductModel.assignments.any(user_id=UUID(user_id)),
                        DataProductModel.assignments.any(
                            decision=DecisionStatus.APPROVED
                        ),
                    )
                )
            )
            .unique()
            .all()
        )

        # Check if any of these data products have access to the dataset
        accessible_through = []
        for dp in user_data_products:
            dataset_links = (
                db.scalars(
                    select(DataProductDatasetAssociation).where(
                        and_(
                            DataProductDatasetAssociation.data_product_id == dp.id,
                            DataProductDatasetAssociation.dataset_id
                            == UUID(dataset_id),
                            DataProductDatasetAssociation.status
                            == DecisionStatus.APPROVED,
                        )
                    )
                )
                .unique()
                .all()
            )

            if dataset_links:
                accessible_through.append(
                    {
                        "data_product_id": str(dp.id),
                        "data_product_name": dp.name,
                        "data_product_namespace": dp.namespace,
                        "approved_on": (
                            dataset_links[0].approved_on.isoformat()
                            if dataset_links[0].approved_on
                            else None
                        ),
                    }
                )

        result = {
            "user_id": user_id,
            "dataset_id": dataset_id,
            "has_access": len(accessible_through) > 0,
            "accessible_through": accessible_through,
        }

        return result
    finally:
        db.close()


# ==============================================================================
# PLATFORM & CONFIGURATION
# ==============================================================================


@mcp.tool
def get_available_platforms() -> List[Dict[str, Any]]:
    """
    Get all available platforms and their configurations.
    """
    db = DataPortalMCPUtils.get_db()

    try:
        from sqlalchemy import select

        platforms = db.scalars(select(PlatformModel)).unique().all()

        results = []
        for platform in platforms:
            platform_info = {
                "id": str(platform.id),
                "name": platform.name,
                "description": platform.description,
                "services": [],
            }

            for service in platform.services:
                platform_info["services"].append(
                    {
                        "id": str(service.id),
                        "name": service.name,
                        "description": service.description,
                        "result_string_template": service.result_string_template,
                        "technical_info_template": service.technical_info_template,
                    }
                )

            results.append(platform_info)

        return results
    finally:
        db.close()


# ==============================================================================
# RESOURCE ENDPOINTS
# ==============================================================================


@mcp.resource("data-product://{data_product_id}")
def get_data_product_resource(data_product_id: str) -> str:
    """Get detailed data product information as a resource"""
    details = get_data_product_details(data_product_id)
    return json.dumps(details, indent=2)


@mcp.resource("dataset://{dataset_id}")
def get_dataset_resource(dataset_id: str) -> str:
    """Get detailed dataset information as a resource"""
    details = get_dataset_details(dataset_id)
    return json.dumps(details, indent=2)


@mcp.resource("marketplace://overview")
def get_marketplace_resource() -> str:
    """Get marketplace overview as a resource"""
    overview = get_marketplace_overview()
    return json.dumps(overview, indent=2)


@mcp.resource("lineage://{entity_type}/{entity_id}")
def get_lineage_resource(entity_type: str, entity_id: str) -> str:
    """Get data lineage information as a resource"""
    lineage = get_data_lineage(entity_id, entity_type)
    return json.dumps(lineage, indent=2)


@mcp.resource("search://{query}")
def get_search_resource(query: str) -> str:
    """Get universal search results as a resource"""
    results = universal_search(query)
    return json.dumps(results, indent=2)


@mcp.resource("trending://data")
def get_trending_resource() -> str:
    """Get trending data and analytics as a resource"""
    trending = get_trending_data()
    return json.dumps(trending, indent=2)


# ==============================================================================
# INTELLIGENT PROMPTS
# ==============================================================================


@mcp.prompt("data-discovery")
def data_discovery_prompt(query: str) -> str:
    """Help discover data products and datasets based on user query"""
    return f"""You are a data discovery assistant for a comprehensive data product portal.

User Query: "{query}"

I can help you discover and explore:

🔵 **Data Products** - Governed data initiatives with clear ownership and lifecycle management
🔷 **Datasets** - Logical groupings of data outputs available for consumption with approval workflows
🟦 **Data Outputs** - Technical endpoints like S3 buckets, database tables, APIs, and streaming endpoints

**Available Discovery Tools:**
- `universal_search(query)` - Search across all entities simultaneously
- `search_data_products(name_filter, domain_filter, status_filter)` - Find specific data products
- `search_datasets(name_filter, domain_filter, access_type_filter)` - Discover available datasets
- `get_marketplace_overview()` - Browse marketplace statistics and featured content
- `get_trending_data()` - See what's popular and actively used
- `get_data_lineage(entity_id, entity_type)` - Understand data relationships and dependencies

**Detailed Investigation Tools:**
- `get_data_product_details(id)` - Deep dive into data product information
- `get_dataset_details(id)` - Explore dataset specifications and access requirements
- `get_data_product_outputs(id)` - See what data outputs a product provides
- `get_dataset_data_outputs(id)` - View technical endpoints for a dataset

Based on your query, I'll help you find the most relevant data assets and guide you through the discovery process."""


@mcp.prompt("access-guidance")
def access_guidance_prompt(user_id: str, dataset_id: str = None) -> str:
    """Guide user through data access and permissions"""

    if dataset_id:
        access_info = check_dataset_access(user_id, dataset_id)
        access_status = "✅ GRANTED" if access_info["has_access"] else "❌ NOT GRANTED"

        return f"""Data Access Guidance System

**User:** {user_id}
**Dataset:** {dataset_id}
**Current Access:** {access_status}

{f"🎯 **Access Details:** You have access through: {', '.join([dp['data_product_name'] for dp in access_info['accessible_through']])}" if access_info["has_access"] else ""}

**How Data Access Works:**
1. **Join a Data Product Team** - Get assigned to a data product with appropriate role
2. **Request Dataset Access** - Your data product must request access to specific datasets
3. **Approval Process** - Dataset owners review and approve access requests
4. **Governed Usage** - Access is scoped to your data product's approved use case

**Next Steps:**
{f"- Use `get_dataset_details('{dataset_id}')` to learn more about this dataset" if dataset_id else ""}
- Use `get_user_recommendations('{user_id}')` for personalized dataset suggestions
- Use `search_datasets()` to discover publicly available datasets
- Contact dataset owners through the portal for access requests

**Available Tools:**
- `check_dataset_access(user_id, dataset_id)` - Check your access to any dataset
- `get_user_recommendations(user_id)` - Get personalized suggestions
- `get_dataset_details(dataset_id)` - Learn about dataset requirements"""

    else:
        return f"""Data Access Guidance System

**User:** {user_id}

Welcome to the data access guidance system! I can help you:

🔍 **Discover Data** - Find datasets relevant to your work
🔐 **Check Access** - Verify your permissions for specific datasets
📋 **Get Recommendations** - Receive personalized dataset suggestions
📊 **Understand Usage** - Learn how data access works in the portal

**Quick Actions:**
- Use `get_user_recommendations('{user_id}')` for personalized suggestions
- Use `check_dataset_access('{user_id}', 'dataset_id')` to verify access
- Use `search_datasets()` to browse available datasets
- Use `get_marketplace_overview()` to explore the data catalog

Data access is always governed through data product teams and requires appropriate approvals."""


@mcp.prompt("lineage-analysis")
def lineage_analysis_prompt(entity_id: str, entity_type: str) -> str:
    """Analyze data lineage and dependencies"""
    lineage = get_data_lineage(entity_id, entity_type)

    upstream_count = len(lineage.get("upstream", []))
    downstream_count = len(lineage.get("downstream", []))

    return f"""Data Lineage Analysis Assistant

**Entity:** {lineage['entity_type'].replace('_', ' ').title()} ({entity_id})
**Upstream Dependencies:** {upstream_count} entities
**Downstream Consumers:** {downstream_count} entities

**Lineage Summary:**
{f"⬆️ **Upstream Sources:** {', '.join([f'{item['name']} ({item['type']})' for item in lineage['upstream'][:3]])}" if upstream_count > 0 else "⬆️ **Upstream Sources:** None (this is a source entity)"}
{f"⬇️ **Downstream Consumers:** {', '.join([f'{item['name']} ({item['type']})' for item in lineage['downstream'][:3]])}" if downstream_count > 0 else "⬇️ **Downstream Consumers:** None (this is a sink entity)"}

**Impact Analysis:**
- Changes to this entity may affect {downstream_count} downstream consumer(s)
- This entity depends on {upstream_count} upstream source(s)
- {"High impact - many dependencies" if (upstream_count + downstream_count) > 5 else "Moderate impact" if (upstream_count + downstream_count) > 2 else "Low impact - few dependencies"}

**Available Actions:**
- Use `get_data_lineage(entity_id, entity_type)` for complete lineage details
- Use `get_data_product_details()` or `get_dataset_details()` for entity information
- Use `universal_search()` to find related entities

Understanding data lineage helps with impact analysis, troubleshooting, and compliance tracking."""


@mcp.prompt("marketplace-exploration")
def marketplace_exploration_prompt() -> str:
    """Guide marketplace exploration and discovery"""
    overview = get_marketplace_overview()
    trending = get_trending_data()

    total_assets = (
        overview["overview"]["total_data_products"]
        + overview["overview"]["total_datasets"]
    )

    return f"""Data Marketplace Exploration Guide

**Marketplace Overview:**
📊 **{total_assets:,}** Total Data Assets Available
- 🔵 {overview['overview']['total_data_products']:,} Data Products
- 🔷 {overview['overview']['total_datasets']:,} Datasets
- 🟦 {overview['overview']['total_data_outputs']:,} Data Outputs
- 🏢 {overview['overview']['total_domains']:,} Business Domains

**Top Domains:**
{chr(10).join([f"• {domain['name']} ({domain['data_product_count']} products)" for domain in overview['top_domains'][:3]])}

**Trending This Week:**
{chr(10).join([f"📈 {item['name']} ({item['access_count']} new access requests)" for item in trending['trending_datasets'][:3]])}

**Exploration Tools:**
- `universal_search("keyword")` - Search across all data assets
- `get_marketplace_overview()` - Get complete marketplace statistics
- `get_trending_data(days=7)` - See what's popular and active
- `search_data_products(domain_filter="domain_name")` - Browse by domain
- `search_datasets(access_type_filter="public")` - Find publicly available data

**Getting Started:**
1. Browse by domain or search for keywords related to your use case
2. Check trending datasets for popular and well-maintained assets
3. Review public datasets for immediate access opportunities
4. Use lineage tools to understand data relationships

The marketplace is your gateway to discovering valuable data assets across the organization!"""


if __name__ == "__main__":
    print(f"Starting {MCP_CONFIG['server_name']} v{MCP_CONFIG['version']}")
    print(f"Capabilities: {', '.join(MCP_CONFIG['capabilities'])}")
    # mcp.run(transport="sse", host="0.0.0.0", port=9000, path="/mcp")
    mcp.run()
