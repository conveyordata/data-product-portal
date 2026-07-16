from contextlib import asynccontextmanager
from typing import Any, Optional, Sequence
from uuid import UUID

import jwt as pyjwt
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.dependencies import get_access_token
from sqlalchemy import select as sa_select
from sqlalchemy.orm import Session, configure_mappers

from app.authorization.role_assignments.data_product.schema import (
    DataProductRoleAssignmentResponse as DataProductRoleAssignmentResponse,
)
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
from app.configuration.domains.schema_response import GetDomainResponse, GetDomainsItem
from app.configuration.domains.service import DomainService
from app.core.auth.auth import get_authenticated_user
from app.core.auth.jwt import get_oidc
from app.core.logging import logger
from app.data_products.output_ports.schema_response import (
    GetOutputPortResponse,
    OutputPortsGet,
)
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_response import (
    GetDataProductResponse,
    GetDataProductsResponseItem,
)
from app.data_products.service import DataProductService
from app.data_products.technical_assets.model import ensure_technical_asset_exists
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)
from app.data_products.technical_assets.service import DataOutputService
from app.database.database import SessionLocal
from app.search_output_ports.schema_response import SearchOutputPortsResponseItem
from app.settings import settings
from app.users.model import User as UserModel


@asynccontextmanager
async def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def initialize_models():
    """Initialize all SQLAlchemy models and resolve relationships"""
    try:
        configure_mappers()
    except Exception as e:
        logger.warn(f"Warning during model initialization: {e}")


initialize_models()


class PortalOIDCProxy(OIDCProxy):
    async def _extract_upstream_claims(
        self, idp_tokens: dict[str, Any]
    ) -> dict[str, Any] | None:
        for key in ("id_token", "access_token"):
            raw = idp_tokens.get(key, "")
            if not raw:
                continue
            try:
                claims = pyjwt.decode(raw, options={"verify_signature": False})
                extracted = {
                    k: claims[k]
                    for k in ("sub", "email", "name", "family_name")
                    if k in claims
                }
                if extracted.get("sub"):
                    logger.debug(
                        f"[MCP] Extracted upstream claims from {key}: "
                        f"sub={extracted.get('sub')!r}, email={extracted.get('email')!r}"
                    )
                    return extracted
            except Exception as exc:
                logger.error(f"[MCP] Could not decode {key} as JWT: {exc}")
        logger.warning(
            "[MCP] _extract_upstream_claims: no usable token found in IDP response"
        )
        return None


def get_auth_provider() -> Optional[PortalOIDCProxy]:
    if settings.OIDC_ENABLED:
        oidc = get_oidc()
        return PortalOIDCProxy(
            config_url=f"{oidc.authority}/.well-known/openid-configuration",
            client_id=oidc.client_id,
            client_secret=oidc.client_secret,
            base_url=f"{settings.HOST.rstrip('/')}/mcp",
            require_authorization_consent="external",
            allowed_client_redirect_uris=settings.MCP_AUTH_REDIRECT_URIS,
        )
    logger.debug("[MCP] OIDC disabled — MCP server will run without authentication")
    return None


mcp = FastMCP(
    name="DataProductPortalMCP",
    instructions="""
    Portal for discovering and exploring data products and output ports.

    Recommended discovery flow:
    1. get_marketplace_overview: understand what's available and get domain IDs
    2. search_output_ports: find specific output ports (preferred for most searches)
       Use search_data_products only when the user explicitly asks to find a data product.
    3. get_*_details: drill into a specific result by UUID

    Output ports (datasets) are the primary way data is shared in the portal.
    Data products are containers owned by teams that group related output ports and technical assets.
    """,
    auth=get_auth_provider(),
)

# ==============================================================================
# CORE DISCOVERY & SEARCH TOOLS
# ==============================================================================


def get_mcp_authenticated_user(db: Session = Depends(get_db_session)) -> UserModel:
    """Get the authenticated portal user from the current MCP request context.

    When OIDC is enabled the FastMCP access token (issued by PortalOIDCProxy)
    carries upstream identity claims extracted from the upstream OIDC id_token.
    These claims are used for a direct DB lookup — no extra userinfo round-trip.

    When OIDC is disabled the default portal user is returned.

    The DB session is injected as a dependency so all ORM attribute reads
    happen inside an active session, avoiding DetachedInstanceError.
    """

    if not settings.OIDC_ENABLED:
        from app.core.auth.auth import generate_default_jwt_token

        logger.debug("[MCP] OIDC disabled — resolving default user")
        return get_authenticated_user(token=generate_default_jwt_token(), db=db)

    access_token = get_access_token()
    if access_token is None:
        logger.warning("[MCP] get_mcp_authenticated_user: no access token in context")
        raise ValueError("No access token found in MCP context")

    logger.debug(
        f"[MCP] Access token present: client_id={access_token.client_id!r}, "
        f"scopes={access_token.scopes!r}, has_claims={bool(access_token.claims)}"
    )

    # OIDCProxy embeds upstream identity under claims["upstream_claims"]
    upstream_claims = (
        access_token.claims.get("upstream_claims") if access_token.claims else None
    )
    if not upstream_claims:
        raise ValueError("No upstream_claims found in access token")

    sub = upstream_claims.get("sub")
    if not sub:
        raise ValueError(f"upstream_claims missing 'sub' claim: {upstream_claims!r}")
    logger.debug(f"[MCP] Resolving user from upstream_claims: sub={sub!r}")

    user_model = db.scalar(sa_select(UserModel).where(UserModel.external_id == sub))
    if not user_model:
        logger.error(f"[MCP] Authenticated user not found in DB: sub={sub!r}")
        raise ValueError(f"Authenticated user not found: sub={sub!r}")

    logger.debug(f"[MCP] Resolved user from upstream_claims: sub={sub!r}")
    return user_model


@mcp.tool
async def get_current_user(
    user: UserModel = Depends(get_mcp_authenticated_user),
) -> dict[str, Any]:
    """Get the profile of the currently authenticated user (id, name, email).
    Use this to resolve 'me' or 'my' in user requests before querying roles or owned resources.
    Requires authentication."""
    return {
        "id": user.id,
        "external_id": user.external_id,
        "first_name": user.first_name,
        "email": user.email,
        "last_name": user.last_name,
    }


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

    # Search output ports - get all and filter manually
    if "output_ports" in search_types:
        all_output_ports = OutputPortService(db).search_output_ports(
            query=None, limit=1000, user=user, current_user_assigned=False
        )
        # Filter by query manually
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

    # Search technical assets - get all and filter manually
    if "technical_assets" in search_types:
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
            GetTechnicalAssetsResponseItem.model_validate(do)
            for do in filtered_data_outputs
        ]
        query_results.update({"technical_assets": result_data_outputs})
        total_count += len(filtered_data_outputs)

    # Search Domains - get all and filter manually
    if "domains" in search_types:
        all_domains = DomainService(db).get_domains()
        # Filter by query manually
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
    # Get all data products and filter manually
    all_data_products = DataProductService(db).get_data_products()
    filtered_data_products = []

    for dp in all_data_products:
        # Apply filters manually
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

        filtered_data_products.append(GetDataProductsResponseItem.model_validate(dp))
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


@mcp.tool(
    description="""
    Search output ports (datasets) using semantic search. This is the preferred tool for finding data in the portal.
    Use this for any question about finding datasets, tables, or data sources — unless the user explicitly asks for a data product.

    An output port is a published, consumable dataset exposed by a data product.
    Returns the name, description, access type, owner, and parent data product for each result.

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
    # Get all datasets and filter manually
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


# ==============================================================================
# DETAILED ENTITY INFORMATION
# ==============================================================================


@mcp.tool(
    description="""
    Get full details of a single data product by its UUID, including its description,
    domain, lifecycle status, owners, output ports, and technical assets.
    Use after search_data_products or search_output_ports to drill into a related data product.

    Args:
        data_product_id: UUID obtained from search_data_products or universal_search.
    """
)
def get_data_product_details(
    data_product_id: str,
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    data_product = DataProductService(db).get_data_product(
        id=UUID(data_product_id),
    )
    return GetDataProductResponse.model_validate(data_product).model_dump()


@mcp.tool(
    description="""
    Get full details of a single output port by its UUID, including schema, access type,
    the data product it belongs to, and owner contact information.
    Use after search_output_ports to get complete information about a specific dataset.

    Args:
        output_port_id: UUID obtained from search_output_ports or universal_search.
    """
)
def get_output_port_details(
    output_port_id: str,
    db: Session = Depends(get_db_session),
    user: UserModel = Depends(get_mcp_authenticated_user),
) -> dict[str, Any]:
    dataset = OutputPortService(db).get_visible_output_port(
        id=UUID(output_port_id), user=user
    )
    return GetOutputPortResponse.model_validate(dataset).model_dump()


@mcp.tool(
    description="""
    Get full details of a specific technical asset (data output) by its UUID,
    including its type, configuration, and the data product it belongs to.

    Args:
        technical_asset_id: UUID obtained from universal_search or get_data_product_analytics.
    """
)
def get_technical_asset_details(
    technical_asset_id: str,
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    do = ensure_technical_asset_exists(UUID(technical_asset_id), db=db)
    data_output = DataOutputService(db).get_data_output(
        do.owner_id,
        id=UUID(technical_asset_id),
    )
    return GetTechnicalAssetsResponseItem.model_validate(data_output).model_dump()


@mcp.tool(
    description="""
    Get details of a specific domain by its UUID, including its name and description.
    Use get_marketplace_overview first to discover available domain IDs.

    Args:
        domain_id: UUID obtained from get_marketplace_overview or search results.
    """
)
def get_domain_details(
    domain_id: str, db: Session = Depends(get_db_session)
) -> dict[str, Any]:
    domain = DomainService(db).get_domain(
        id=UUID(domain_id),
    )

    return GetDomainResponse.model_validate(domain).model_dump()


# ==============================================================================
# MARKETPLACE & ANALYTICS
# ==============================================================================


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
    # Get counts by querying all and taking length
    all_data_products = DataProductService(db).get_data_products()
    all_output_ports = OutputPortService(db).search_output_ports(
        query=None, limit=1000, user=user, current_user_assigned=False
    )
    all_technical_assets = DataOutputService(db).get_data_outputs()
    all_domains = DomainService(db).get_domains()

    # Get first 5 items as "popular" (since we can't sort)
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
            GetDomainsItem.model_validate(domain).model_dump() for domain in all_domains
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
    # Get the data product using service
    data_product = DataProductService(db).get_data_product(
        id=UUID(data_product_id),
    )

    if not data_product:
        return {"error": f"Data product {data_product_id} not found"}

    # Get related datasets - filter manually from all datasets
    output_ports = OutputPortService(db).get_output_ports(
        user=user, data_product_id=UUID(data_product_id)
    )

    # Get related data outputs - filter manually from all data outputs
    technical_assets = DataOutputService(db).get_data_outputs()
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
                OutputPortsGet.model_validate(ds).model_dump() for ds in output_ports
            ],
            "technical_assets": [
                GetTechnicalAssetsResponseItem.model_validate(do).model_dump()
                for do in related_technical_assets
            ],
        },
    }


# ==============================================================================
# RESOURCE ENDPOINTS
# ==============================================================================


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

    # Convert to Pydantic model and then to formatted string
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
    "output-port://{output_port_id}", description="""Get output port as a resource."""
)
def get_output_port_resource(
    output_port_id: str,
    db: Session = Depends(get_db_session),
    user: UserModel = Depends(get_mcp_authenticated_user),
) -> str:
    output_port = OutputPortService(db).get_visible_output_port(
        id=UUID(output_port_id), user=user
    )

    if not output_port:
        return f"Error: Output port {output_port_id} not found"
    # Convert to Pydantic model and then to formatted string
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
    "marketplace://overview", description="""Get marketplace overview as a resource."""
)
def get_marketplace_resource(
    db: Session = Depends(get_db_session),
    user: UserModel = Depends(get_mcp_authenticated_user),
) -> str:
    overview = get_marketplace_overview(db, user)

    if "error" in overview:
        return f"Error: {overview['error']}"

    stats = overview["statistics"]

    return f"""
# Data Product Portal - Marketplace Overview

## Statistics
- **Data Products:** {stats["total_data_products"]}
- **Output Ports:** {stats["total_datasets"]}
- **Technical Assets:** {stats["total_data_outputs"]}
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

## Popular Output Ports
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


# ==============================================================================
# USER ROLES & PERMISSIONS
# ==============================================================================


@mcp.tool(
    description="""
    Get role assignments for a user across the portal.
    Use get_current_user first to resolve 'me' or 'my' to a user ID.
    Requires authentication.

    Args:
        user_id: UUID of the user. Defaults to the currently authenticated user.
        scope_type: Filter by scope. Valid values: 'global' (portal-wide roles),
                    'data_product' (roles on specific data products),
                    'dataset' (roles on specific output ports). Leave empty to return all scopes.
        limit: Maximum number of role assignments to return.
    """
)
def get_user_roles(
    user_id: Optional[str] = None,
    scope_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db_session),
    current_user: UserModel = Depends(get_mcp_authenticated_user),
) -> dict[str, Any]:

    # Use current user if no user_id specified
    target_user_id = user_id or str(current_user.id)

    # Get role assignments using the different service classes
    global_roles: list[dict[str, Any]] = []
    data_product_roles: dict[str, list[dict[str, Any]]] = {}
    dataset_roles: dict[str, list[dict[str, Any]]] = {}

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
            "output_ports": dataset_roles,
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


@mcp.tool
def get_resource_roles(
    resource_type: str,
    resource_id: str,
    limit: int = 50,
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    """
    List all users and their roles on a specific data product or output port.

    Args:
        resource_type: Type of resource. Valid values: 'data_product' or 'dataset' (output ports use 'dataset').
        resource_id: UUID of the resource.
        limit: Maximum number of role assignments to return.
    """
    resource_uuid = UUID(resource_id)

    # Get role assignments based on resource type
    assignment_responses: list[dict[str, Any]] = []
    if resource_type == "data_product":
        assignments = DataProductRoleAssignmentService(db).list_assignments(
            data_product_id=resource_uuid
        )
        assignment_responses = [
            DataProductRoleAssignmentResponse.model_validate(assignment).model_dump()
            for assignment in assignments[:limit]
        ]
    elif resource_type == "dataset":
        assignments = DatasetRoleAssignmentService(db).list_assignments(
            dataset_id=resource_uuid
        )
        assignment_responses = [
            DatasetRoleAssignmentResponse.model_validate(assignment).model_dump()
            for assignment in assignments[:limit]
        ]
    else:
        return {
            "error": f"Invalid resource_type: {resource_type}.\
                    Must be 'data_product' or 'dataset'"
        }

    # Group by role for better organization
    roles_by_type: dict[str, list[dict[str, Any]]] = {}
    users_with_roles: list[dict[str, Any]] = []

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
