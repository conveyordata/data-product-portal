from typing import Any, Dict, Optional
from uuid import UUID

from fastmcp import Context, FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import AccessToken, get_access_token
from sqlalchemy.orm import configure_mappers

from app.authorization.role_assignments.data_product.schema import (
    DataProductRoleAssignmentResponse as DataProductRoleAssignmentResponse,
)

# Add role assignment imports
from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.authorization.role_assignments.global_.schema import (
    GlobalRoleAssignmentResponse as GlobalRoleAssignmentResponse,
)
from app.authorization.role_assignments.global_.service import (
    RoleAssignmentService as GlobalRoleAssignmentService,
)
from app.authorization.role_assignments.output_port.schema import (
    OutputPortRoleAssignmentResponse as DatasetRoleAssignmentResponse,
)
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.configuration.domains.schema_response import DomainGetOld
from app.configuration.domains.service import DomainService
from app.core.auth.auth import get_authenticated_user
from app.core.auth.jwt import JWTToken, get_oidc
from app.core.logging import logger
from app.data_products.output_ports.schema_response import DatasetGet, DatasetsGet
from app.data_products.output_ports.service import OutputPortService

# Import enums - corrected paths
from app.data_products.schema_response import (
    DataProductGet,
    DataProductsGet,
    GetDataProductsResponseItem,
)
from app.data_products.service import DataProductService
from app.data_products.technical_assets.model import ensure_data_output_exists

# Import Pydantic schemas - corrected paths
from app.data_products.technical_assets.schema_response import (
    DataOutputGet,
    DataOutputsGet,
)

# Import existing services
from app.data_products.technical_assets.service import DataOutputService
from app.database.database import get_db_session
from app.settings import settings


def initialize_models():
    """Initialize all SQLAlchemy models and resolve relationships"""
    try:
        configure_mappers()
    except Exception as e:
        logger.warn(f"Warning during model initialization: {e}")


initialize_models()


def get_auth_provider() -> Optional[JWTVerifier]:
    if settings.OIDC_ENABLED:
        return JWTVerifier(issuer=get_oidc().authority, jwks_uri=get_oidc().jwks_uri)
    return None


mcp = FastMCP(name="DataProductPortalMCP", auth=get_auth_provider())

# ==============================================================================
# CORE DISCOVERY & SEARCH TOOLS
# ==============================================================================


def get_mcp_authenticated_user(token: str):
    user = get_authenticated_user(
        token=JWTToken(sub="", token=f"Bearer {token}"), db=next(get_db_session())
    )
    return {
        "id": user.id,
        "external_id": user.external_id,
        "first_name": user.first_name,
        "email": user.email,
        "last_name": user.last_name,
    }


@mcp.tool
async def get_current_user(ctx: Context) -> dict[str, Any]:
    """Get current user data from the MCP. You can use this to
    get information about the authenticated user."""
    token = get_access_token()
    return get_mcp_authenticated_user(token=token.token)


@mcp.tool
def universal_search(
    query: str, entity_types: list[str] = [], limit: int = 10
) -> Dict[str, Any]:
    """
    Universal search across data products, datasets, and data outputs.

    Args:
        query: Search query string
        entity_types: List of entity types to search
        (data_products, datasets, data_outputs, domains)
        limit: Maximum number of results per entity type
    """
    try:
        access_token: AccessToken = get_access_token()

        db = next(get_db_session())
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            results = {
                "query": query,
                "results": {},
                "total_count": 0,
            }
            total_count = 0
            search_types = entity_types or [
                "data_products",
                "datasets",
                "data_outputs",
                "domains",
            ]
            query_results = {}
            # Search Data Products - get all and filter manually
            if "data_products" in search_types:
                all_data_products = DataProductService(db).get_data_products()
                # Filter by query manually
                filtered_data_products = []
                for dp in all_data_products:
                    if query.lower() in dp.name.lower() or (
                        dp.description and query.lower() in dp.description.lower()
                    ):
                        filtered_data_products.append(
                            DataProductsGet.model_validate(dp).convert()
                        )
                        if len(filtered_data_products) >= limit:
                            break

                result_data_products = [
                    GetDataProductsResponseItem.model_validate(dp).model_dump()
                    for dp in filtered_data_products
                ]
                query_results.update({"data_products": result_data_products})
                total_count += len(filtered_data_products)

            # Search Datasets - get all and filter manually
            if "datasets" in search_types:
                all_datasets = OutputPortService(db).get_datasets(user=user)
                # Filter by query manually
                filtered_datasets = []
                for ds in all_datasets:
                    if query.lower() in ds.name.lower() or (
                        ds.description and query.lower() in ds.description.lower()
                    ):
                        filtered_datasets.append(ds)
                        if len(filtered_datasets) >= limit:
                            break

                result_datasets = [
                    DatasetsGet.model_validate(ds).model_dump()
                    for ds in filtered_datasets
                ]
                query_results.update({"datasets": result_datasets})
                total_count += len(filtered_datasets)

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

                result_data_outputs = [
                    DataOutputsGet.model_validate(do).model_dump()
                    for do in filtered_data_outputs
                ]
                query_results.update({"data_outputs": result_data_outputs})
                total_count += len(filtered_data_outputs)

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

                result_domains = [
                    DomainGetOld.model_validate(domain).model_dump()
                    for domain in filtered_domains
                ]
                query_results.update({"domains": result_domains})
                total_count += len(filtered_domains)
            results["total_count"] = total_count
            results["results"] = query_results
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

                filtered_data_products.append(
                    DataProductsGet.model_validate(dp).convert()
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
        access_token: AccessToken = get_access_token()
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            # Get all datasets and filter manually
            all_datasets = OutputPortService(db).get_datasets(user=user)
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
            data_product = DataProductService(db).get_data_product_old(
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
        access_token: AccessToken = get_access_token()
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            dataset = OutputPortService(db).get_dataset(id=UUID(dataset_id), user=user)

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
        do = ensure_data_output_exists(UUID(data_output_id), db=db)
        try:
            data_output = DataOutputService(db).get_data_output(
                do.owner_id,
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

            return DomainGetOld.model_validate(domain).model_dump()
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
        access_token: AccessToken = get_access_token()
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            # Get counts by querying all and taking length
            all_data_products = DataProductService(db).get_data_products()
            all_datasets = OutputPortService(db).get_datasets(user=user)
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
                        GetDataProductsResponseItem.model_validate(
                            DataProductsGet.model_validate(dp).convert()
                        ).model_dump()
                        for dp in popular_data_products
                    ],
                    "popular_datasets": [
                        DatasetsGet.model_validate(ds).model_dump()
                        for ds in popular_datasets
                    ],
                },
                "domains": [
                    DomainGetOld.model_validate(domain).model_dump()
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
        access_token: AccessToken = get_access_token()
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            # Get the data product using service
            data_product = DataProductService(db).get_data_product_old(
                id=UUID(data_product_id),
            )

            if not data_product:
                return {"error": f"Data product {data_product_id} not found"}

            # Get related datasets - filter manually from all datasets
            all_datasets = OutputPortService(db).get_datasets(user=user)
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
                "data_product": DataProductGet.model_validate(
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
            data_product = DataProductService(db).get_data_product_old(
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
**Domain:** {dp_data.domain.name if dp_data.domain else "N/A"}
**Description:** {dp_data.description or "No description available"}

## Metadata
- **Created:** {dp_data.created_at}
- **Updated:** {dp_data.updated_at}
- **Owner:** {dp_data.owner_email or "N/A"}

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
        access_token: AccessToken = get_access_token()
        user = get_mcp_authenticated_user(token=access_token.token)
        try:
            dataset = OutputPortService(db).get_dataset(id=UUID(dataset_id), user=user)

            if not dataset:
                return f"Error: Dataset {dataset_id} not found"
            # Convert to Pydantic model and then to formatted string
            ds_data = DatasetGet.model_validate(dataset)

            return f"""
# Dataset: {ds_data.name}

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
- **Data Products:** {stats["total_data_products"]}
- **Datasets:** {stats["total_datasets"]}
- **Data Outputs:** {stats["total_data_outputs"]}
- **Domains:** {stats["total_domains"]}

## Popular Data Products
{
            chr(10).join(
                [
                    f"- {dp['name']} ({dp['status']})"
                    for dp in overview["featured_content"]["popular_data_products"]
                ]
            )
        }

## Popular Datasets
{
            chr(10).join(
                [
                    f"- {ds['name']} ({ds.get('access_type', 'N/A')})"
                    for ds in overview["featured_content"]["popular_datasets"]
                ]
            )
        }

## Available Domains
{
            chr(10).join(
                [
                    f"- {domain['name']}: {domain['description'] or 'No description'}"
                    for domain in overview["domains"]
                ]
            )
        }
"""

    except Exception as e:
        return f"Error retrieving marketplace overview: {str(e)}"


# ==============================================================================
# USER ROLES & PERMISSIONS
# ==============================================================================


@mcp.tool
def get_user_roles(
    user_id: Optional[str] = None,
    scope_type: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get user roles and role assignments.

    Args:
        user_id: Specific user ID to get roles for (optional, defaults to current user)
        scope_type: Filter by scope type ('global', 'data_product', 'dataset')
        limit: Maximum number of role assignments to return
    """
    try:
        db = next(get_db_session())
        access_token: AccessToken = get_access_token()
        current_user = get_mcp_authenticated_user(token=access_token.token)

        try:
            # Use current user if no user_id specified
            target_user_id = user_id or str(current_user["id"])

            # Get role assignments using the different service classes
            global_roles: list[Dict[str, Any]] = []
            data_product_roles: Dict[str, list[Dict[str, Any]]] = {}
            dataset_roles: Dict[str, list[Dict[str, Any]]] = {}

            # Get global roles if not filtered or if specifically requested
            if not scope_type or scope_type == "global":
                global_role_service = GlobalRoleAssignmentService(db)
                global_assignments = global_role_service.list_assignments(
                    user_id=UUID(target_user_id)
                )
                global_roles = [
                    GlobalRoleAssignmentResponse.model_validate(assignment).model_dump()
                    for assignment in global_assignments[:limit]
                ]

            # Get data product roles if not filtered or if specifically requested
            if not scope_type or scope_type == "data_product":
                data_product_role_service = DataProductRoleAssignmentService(db)
                dp_assignments = data_product_role_service.list_assignments(
                    user_id=UUID(target_user_id)
                )

                for assignment in dp_assignments[:limit]:
                    assignment_data = DataProductRoleAssignmentResponse.model_validate(
                        assignment
                    ).model_dump()
                    dp_id = str(assignment.data_product_id)
                    if dp_id not in data_product_roles:
                        data_product_roles[dp_id] = []
                    data_product_roles[dp_id].append(assignment_data)

            # Get dataset roles if not filtered or if specifically requested
            if not scope_type or scope_type == "dataset":
                dataset_role_service = DatasetRoleAssignmentService(db)
                dataset_assignments = dataset_role_service.list_assignments(
                    user_id=UUID(target_user_id)
                )

                for assignment in dataset_assignments[:limit]:
                    assignment_data = DatasetRoleAssignmentResponse.model_validate(
                        assignment
                    ).model_dump()
                    ds_id = str(assignment.dataset_id)
                    if ds_id not in dataset_roles:
                        dataset_roles[ds_id] = []
                    dataset_roles[ds_id].append(assignment_data)

            total_assignments = (
                len(global_roles)
                + sum(len(roles) for roles in data_product_roles.values())
                + sum(len(roles) for roles in dataset_roles.values())
            )

            return {
                "user_id": target_user_id,
                "is_current_user": target_user_id == str(current_user["id"]),
                "total_assignments": total_assignments,
                "roles": {
                    "global": global_roles,
                    "data_products": data_product_roles,
                    "datasets": dataset_roles,
                },
                "filters_applied": {
                    "scope_type": scope_type,
                },
                "summary": {
                    "global_roles_count": len(global_roles),
                    "data_product_roles_count": len(data_product_roles),
                    "dataset_roles_count": len(dataset_roles),
                },
            }

        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get user roles: {str(e)}"}


@mcp.tool
def get_resource_roles(
    resource_type: str,
    resource_id: str,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Get all user roles for a specific resource (data product or dataset).

    Args:
        resource_type: Type of resource ('data_product' or 'dataset')
        resource_id: ID of the resource
        limit: Maximum number of role assignments to return
    """
    try:
        db = next(get_db_session())

        try:
            resource_uuid = UUID(resource_id)

            # Get role assignments based on resource type
            assignment_responses: list[Dict[str, Any]] = []
            if resource_type == "data_product":
                assignments = DataProductRoleAssignmentService(db).list_assignments(
                    data_product_id=resource_uuid
                )
                assignment_responses = [
                    DataProductRoleAssignmentResponse.model_validate(
                        assignment
                    ).model_dump()
                    for assignment in assignments[:limit]
                ]
            elif resource_type == "dataset":
                assignments = DatasetRoleAssignmentService(db).list_assignments(
                    dataset_id=resource_uuid
                )
                assignment_responses = [
                    DatasetRoleAssignmentResponse.model_validate(
                        assignment
                    ).model_dump()
                    for assignment in assignments[:limit]
                ]
            else:
                return {
                    "error": f"Invalid resource_type: {resource_type}.\
                        Must be 'data_product' or 'dataset'"
                }

            # Group by role for better organization
            roles_by_type: Dict[str, list[Dict[str, Any]]] = {}
            users_with_roles: list[Dict[str, Any]] = []

            for assignment_data in assignment_responses:
                role_info = assignment_data.get("role", {})
                role_name = (
                    role_info.get("name", "Unknown")
                    if isinstance(role_info, dict)
                    else "Unknown"
                )
                if role_name not in roles_by_type:
                    roles_by_type[role_name] = []
                roles_by_type[role_name].append(assignment_data)

                users_with_roles.append(
                    {
                        "user_id": assignment_data.get("user_id"),
                        "role_name": role_name,
                        "assignment_id": assignment_data.get("id"),
                        "created_at": assignment_data.get("created_at"),
                    }
                )

            return {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "total_assignments": len(assignment_responses),
                "roles_by_type": roles_by_type,
                "users_with_roles": users_with_roles,
                "summary": {
                    "unique_roles": list(roles_by_type.keys()),
                    "total_users": len(users_with_roles),
                },
            }

        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get resource roles: {str(e)}"}
