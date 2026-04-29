from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from fastmcp import Context, FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token
from sqlalchemy import select as sql_select
from sqlalchemy.orm import configure_mappers

from app.authorization.role_assignments.data_product.schema import (
    DataProductRoleAssignmentResponse as DataProductRoleAssignmentResponse,
)
from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService as DataProductRoleAssignmentService,
)
from app.authorization.role_assignments.enums import DecisionStatus
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
from app.authorization.roles.schema import Prototype
from app.configuration.domains.schema_response import GetDomainResponse, GetDomainsItem
from app.configuration.domains.service import DomainService
from app.core.auth.auth import get_authenticated_user
from app.core.auth.jwt import JWTToken, get_oidc
from app.core.logging import logger
from app.data_products.output_ports.cost.service import OutputPortCostService
from app.data_products.output_ports.freshness.enums import FreshnessStatus
from app.data_products.output_ports.input_ports.model import (
    InputPort as InputPortModel,
)
from app.data_products.output_ports.query_stats.service import (
    OutputPortStatsService,
    QueryStatsGranularity,
)
from app.data_products.output_ports.schema_response import (
    DatasetsGet,
    GetOutputPortResponse,
    OutputPortsGet,
)
from app.data_products.output_ports.semantic_models.schema_response import (
    SemanticModelResponse,
)
from app.data_products.output_ports.semantic_models.service import SemanticModelService
from app.data_products.output_ports.service import OutputPortService
from app.data_products.output_ports.table_schemas.schema_response import (
    TableSchemaResponse,
)
from app.data_products.output_ports.table_schemas.service import TableSchemaService
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
from app.database.database import get_db_session
from app.graph.service import GraphService
from app.search_output_ports.schema_response import SearchDatasets
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


mcp = FastMCP(
    name="DataProductPortalMCP",
    instructions="""
    Portal for discovering and exploring data products and output ports.

    Recommended discovery flow:
    1. get_marketplace_overview: understand what's available and get domain IDs
    2. search_output_ports: find specific output ports (preferred for most searches)
       Use search_data_products only when the user explicitly asks to find a data product.
    3. get_*_details: drill into a specific result by UUID
    4. get_data_product_usage: get cost breakdown and top consumer query stats for a data product
    5. get_lineage_graph: traverse the full data lineage graph to answer connection-based
       questions (deprecation impact, upstream/downstream dependencies, transitive consumers).
       Edges with animated=true are APPROVED access links; animated=false are pending.

    Output ports (datasets) are the primary way data is shared in the portal.
    Data products are containers owned by teams that group related output ports and technical assets.

    Entity hierarchy:
    - Domain → Data Product → Output Port (primary data-sharing unit) / Technical Asset
    - Input Port: the access link between a consuming Data Product and an Output Port;
      has status PENDING | APPROVED | DENIED and a justification.
    - Output ports are always owned by exactly one data product; technical assets likewise.

    For the full entity model, ID provenance, and relationship graph, read resource portal://ontology.
    """,
    auth=get_auth_provider(),
)

# ==============================================================================
# CORE DISCOVERY & SEARCH TOOLS
# ==============================================================================


def get_mcp_authenticated_user(token: Optional[str]):
    if token is None:
        # OIDC disabled — mirror the REST API fallback (auth.py non-OIDC branch)
        jwt_token = JWTToken(sub=settings.DEFAULT_USERNAME, token="")
    else:
        jwt_token = JWTToken(sub="", token=f"Bearer {token}")
    user = get_authenticated_user(token=jwt_token, db=next(get_db_session()))
    return {
        "id": user.id,
        "external_id": user.external_id,
        "first_name": user.first_name,
        "email": user.email,
        "last_name": user.last_name,
    }


def get_current_mcp_user() -> dict:
    access_token = get_access_token()
    return get_mcp_authenticated_user(
        token=access_token.token if access_token else None
    )


def _build_freshness_dict(dataset: Any) -> Dict[str, Any]:
    return {
        "status": dataset.freshness_status or FreshnessStatus.UNKNOWN.value,
        "slo_deadline": dataset.freshness_deadline_time.isoformat()
        if dataset.freshness_deadline_time
        else None,
        "last_refreshed_at": dataset.latest_freshness_at.isoformat()
        if dataset.latest_freshness_at
        else None,
    }


@mcp.tool
async def get_current_user(ctx: Context) -> dict[str, Any]:
    """Get the profile of the currently authenticated user (id, name, email).
    Use this to resolve 'me' or 'my' in user requests before querying roles or owned resources.
    Requires authentication."""
    return get_current_mcp_user()


@mcp.tool
def universal_search(
    query: str, entity_types: list[str] = [], limit: int = 10
) -> Dict[str, Any]:
    """
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
    try:
        db = next(get_db_session())
        user = get_current_mcp_user()
        try:
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
                all_output_ports = OutputPortService(db).get_datasets(user=user)
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
                    GetDataProductsResponseItem.model_validate(ds).model_dump()
                    for ds in filtered_output_ports
                ]
                query_results.update({"datasets": result_datasets})
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
                        domain.description
                        and query.lower() in domain.description.lower()
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
    """
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
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to search data products: {str(e)}"}


@mcp.tool
def search_output_ports(
    query: Optional[str] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Search output ports (datasets) using semantic search. This is the preferred tool for finding data in the portal.
    Use this for any question about finding datasets, tables, or data sources — unless the user explicitly asks for a data product.

    An output port is a published, consumable dataset exposed by a data product.
    Returns the name, description, access type, owner, and parent data product for each result.

    Args:
        query: Natural language or keyword search. Leave empty to list all accessible output ports.
        limit: Maximum number of results to return.
    """
    try:
        db = next(get_db_session())
        user = get_current_mcp_user()
        try:
            # Get all datasets and filter manually
            all_datasets = OutputPortService(db).search_datasets(
                query=query, user=user, limit=limit, current_user_assigned=False
            )
            return {
                "output_ports": [
                    SearchDatasets.model_validate(ds).model_dump()
                    for ds in all_datasets
                ],
                "count": len(all_datasets),
                "filters_applied": {
                    "query": query,
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
    """
    Get full details of a single data product by its UUID, including its description,
    domain, lifecycle status, owners, output ports, and technical assets.
    Use after search_data_products or search_output_ports to drill into a related data product.

    Args:
        data_product_id: UUID obtained from search_data_products or universal_search.
    """
    try:
        db = next(get_db_session())
        try:
            data_product = DataProductService(db).get_data_product(
                id=UUID(data_product_id),
            )

            if not data_product:
                return {"error": f"Data product {data_product_id} not found"}

            # Use Pydantic schema for serialization
            return GetDataProductResponse.model_validate(data_product).model_dump()
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data product details: {str(e)}"}


@mcp.tool
def get_output_port_details(output_port_id: str) -> Dict[str, Any]:
    """
    Get full details of a single output port by its UUID, including schema, access type,
    the data product it belongs to, owner contact information, freshness status, and
    all data product access grants (consuming_data_products).

    The response includes a `freshness` block:
    - `status`: "fresh" | "stale" | "unknown" (always present)
    - `slo_deadline`: SLO deadline as "HH:MM:SS", or null if no SLO is configured
    - `last_refreshed_at`: ISO datetime of the last data refresh, or null if never observed

    The response includes a `consuming_data_products` list — every data product that has
    requested access to this output port, with their justification and decision status
    (PENDING, APPROVED, or DENIED).

    Use after search_output_ports to get complete information about a specific dataset.

    Args:
        output_port_id: UUID obtained from search_output_ports or universal_search.
    """
    try:
        db = next(get_db_session())
        user = get_current_mcp_user()
        try:
            dataset = OutputPortService(db).get_dataset(
                id=UUID(output_port_id), user=user
            )

            if not dataset:
                return {"error": f"Dataset {output_port_id} not found"}

            result = GetOutputPortResponse.model_validate(dataset).model_dump()
            result["freshness"] = _build_freshness_dict(dataset)
            consuming = OutputPortService(db).get_consuming_data_products(
                UUID(output_port_id), dataset.data_product_id
            )
            result["consuming_data_products"] = [
                {
                    "consuming_data_product_id": str(
                        ip.consuming_abstract_data_product_id
                    ),
                    "consuming_data_product_name": ip.consuming_abstract_data_product.name,
                    "status": ip.status.value,
                    "justification": ip.justification,
                    "requested_by_email": ip.requested_by.email
                    if ip.requested_by
                    else None,
                    "approved_by_email": ip.approved_by.email
                    if ip.approved_by
                    else None,
                    "denied_by_email": ip.denied_by.email if ip.denied_by else None,
                    "requested_on": ip.requested_on.isoformat()
                    if ip.requested_on
                    else None,
                    "approved_on": ip.approved_on.isoformat()
                    if ip.approved_on
                    else None,
                    "denied_on": ip.denied_on.isoformat() if ip.denied_on else None,
                }
                for ip in consuming
            ]
            return result
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get dataset details: {str(e)}"}


@mcp.tool
def get_output_port_model(output_port_id: str) -> Dict[str, Any]:
    """
    Get the full data model of a single output port: table schemas with column-level
    tags (including PII classifications) and semantic model definitions.

    Use this to inspect the data structure and semantic metadata of an output port —
    e.g., for compliance analysis, PII discovery, or schema exploration.

    The response includes:
    - `output_port`: name, description, about, access_type, and port-level tags
    - `table_schemas`: list of schemas, each with columns. Column `tags` contain PII
      and sensitivity classifications (e.g. tag value "PII", "SENSITIVE").
      Table-level `tags` contain dataset-level classifications.
    - `semantic_models`: business entity definitions (entities, metrics, dimensions)
      in MetricsFlow or OpenSemanticInterchange format.

    For compliance questions, combine with `get_data_product_details` to get the
    data product's `about` field (legal/compliance context).

    Args:
        output_port_id: UUID obtained from search_output_ports or get_data_product_analytics.
    """
    try:
        db = next(get_db_session())
        user = get_current_mcp_user()
        try:
            dataset = OutputPortService(db).get_dataset(
                id=UUID(output_port_id), user=user
            )
            if not dataset:
                return {"error": f"Output port {output_port_id} not found"}

            table_schemas = TableSchemaService(db).get_all(UUID(output_port_id))
            semantic_models = SemanticModelService(db).get_all(UUID(output_port_id))

            return {
                "output_port": {
                    "id": str(dataset.id),
                    "name": dataset.name,
                    "description": dataset.description,
                    "about": dataset.about,
                    "access_type": dataset.access_type.value
                    if dataset.access_type
                    else None,
                    "tags": [
                        {"id": str(t.id), "value": t.value}
                        for t in (dataset.tags or [])
                    ],
                },
                "table_schemas": [
                    TableSchemaResponse.model_validate(ts).model_dump()
                    for ts in table_schemas
                ],
                "semantic_models": [
                    SemanticModelResponse.model_validate(sm).model_dump()
                    for sm in semantic_models
                ],
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get output port model: {str(e)}"}


@mcp.tool
def get_technical_asset_details(technical_asset_id: str) -> Dict[str, Any]:
    """
    Get full details of a specific technical asset (data output) by its UUID,
    including its type, configuration, and the data product it belongs to.

    Args:
        technical_asset_id: UUID obtained from universal_search or get_data_product_analytics.
    """
    try:
        db = next(get_db_session())
        do = ensure_technical_asset_exists(UUID(technical_asset_id), db=db)
        try:
            data_output = DataOutputService(db).get_data_output(
                do.owner_id,
                id=UUID(technical_asset_id),
            )

            if not data_output:
                return {"error": f"Data output {technical_asset_id} not found"}

            return GetTechnicalAssetsResponseItem.model_validate(
                data_output
            ).model_dump()
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data output details: {str(e)}"}


@mcp.tool
def get_domain_details(domain_id: str) -> Dict[str, Any]:
    """
    Get details of a specific domain by its UUID, including its name and description.
    Use get_marketplace_overview first to discover available domain IDs.

    Args:
        domain_id: UUID obtained from get_marketplace_overview or search results.
    """
    try:
        db = next(get_db_session())
        try:
            domain = DomainService(db).get_domain(
                id=UUID(domain_id),
            )

            if not domain:
                return {"error": f"Domain {domain_id} not found"}

            return GetDomainResponse.model_validate(domain).model_dump()
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get domain details: {str(e)}"}


# ==============================================================================
# MARKETPLACE & ANALYTICS
# ==============================================================================


@mcp.tool
def get_marketplace_overview() -> Dict[str, Any]:
    """
    Get a high-level overview of the portal: total counts of data products, output ports,
    technical assets, a list of all domains with their IDs, and featured content.
    Use this as a starting point to orient the user, discover available domain IDs,
    or answer questions like 'what data is available?'.
    """
    try:
        db = next(get_db_session())
        user = get_current_mcp_user()
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
                    "total_output_ports": len(all_datasets),
                    "total_technical_assets": len(all_data_outputs),
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
                        DatasetsGet.model_validate(ds).model_dump()
                        for ds in popular_datasets
                    ],
                },
                "domains": [
                    GetDomainsItem.model_validate(domain).model_dump()
                    for domain in all_domains
                ],
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get marketplace overview: {str(e)}"}


@mcp.tool
def get_data_product_analytics(data_product_id: str) -> Dict[str, Any]:
    """
    Get analytics for a data product: its output ports, technical assets, and input ports (what this data product consumes from other data products).
    Use this to answer:
    - 'What does this data product expose?' or 'How many output ports does it have?' — see output_ports / technical_assets.
    - 'What does this data product consume and why?' — see input_ports with justification and status.
    - 'Which upstream is stale?' — see input_ports[].freshness.status ('fresh'|'stale'|'unknown').
    - 'Who do I contact about an upstream?' — see input_ports[].owners with name and email.

    Args:
        data_product_id: UUID obtained from search_data_products or get_data_product_details.
    """
    try:
        db = next(get_db_session())
        user = get_current_mcp_user()
        try:
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

            input_port_records = (
                db.scalars(
                    sql_select(InputPortModel).where(
                        InputPortModel.consuming_abstract_data_product_id
                        == UUID(data_product_id)
                    )
                )
                .unique()
                .all()
            )

            dp_role_service = DataProductRoleAssignmentService(db)

            return {
                "data_product": GetDataProductResponse.model_validate(
                    data_product
                ).model_dump(),
                "analytics": {
                    "output_ports_count": len(output_ports),
                    "technical_assets_count": len(related_technical_assets),
                    "output_ports": [
                        OutputPortsGet.model_validate(ds).model_dump()
                        for ds in output_ports
                    ],
                    "technical_assets": [
                        GetTechnicalAssetsResponseItem.model_validate(do).model_dump()
                        for do in related_technical_assets
                    ],
                    "input_ports": [
                        {
                            "output_port_id": str(ip.dataset_id),
                            "output_port_name": ip.dataset.name,
                            "producing_data_product_id": str(
                                ip.dataset.data_product_id
                            ),
                            "producing_data_product_name": ip.dataset.data_product.name,
                            "status": ip.status.value,
                            "justification": ip.justification,
                            "requested_by_email": ip.requested_by.email
                            if ip.requested_by
                            else None,
                            "requested_on": ip.requested_on.isoformat()
                            if ip.requested_on
                            else None,
                            "approved_on": ip.approved_on.isoformat()
                            if ip.approved_on
                            else None,
                            "denied_on": ip.denied_on.isoformat()
                            if ip.denied_on
                            else None,
                            "freshness": _build_freshness_dict(ip.dataset),
                            "owners": [
                                {
                                    "name": f"{a.user.first_name} {a.user.last_name}".strip(),
                                    "email": a.user.email,
                                    "role": a.role.name if a.role else None,
                                }
                                for a in dp_role_service.list_assignments(
                                    data_product_id=ip.dataset.data_product_id,
                                    decision=DecisionStatus.APPROVED,
                                )
                                if a.role and a.role.prototype == Prototype.OWNER
                            ],
                        }
                        for ip in input_port_records
                    ],
                },
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data product analytics: {str(e)}"}


@mcp.tool
def get_lineage_graph() -> Dict[str, Any]:
    """
    Returns the full data lineage graph of the portal: all data products,
    output ports, and the access relationships between them.

    Use this to answer any connection-based question:
    - Which consumers depend on a data product? (deprecation impact)
    - What output ports does a data product consume?
    - Who are the indirect / transitive consumers?

    Nodes have types: 'dataProductNode' or 'datasetNode' (output port).
    Edges represent two kinds of relationships:
    - Data product → output port: ownership (the product exposes that port)
    - Output port → data product: access link
      animated=true  → APPROVED (active dependency)
      animated=false → PENDING/REQUESTED (not yet approved)

    To find consumers affected by deprecating a data product:
    1. Find all 'datasetNode' nodes where data.link_to_id == data_product_id (its output ports)
    2. Find all edges where source == one of those output port ids
    3. The edge targets are the downstream consumers; animated=true means APPROVED access.
    """
    try:
        db = next(get_db_session())
        try:
            graph = GraphService(db).get_graph_data(
                data_product_nodes_enabled=True,
                dataset_nodes_enabled=True,
            )
            return {
                "nodes": [node.model_dump(mode="json") for node in graph.nodes],
                "edges": [edge.model_dump(mode="json") for edge in graph.edges],
            }
        finally:
            db.close()
    except Exception as e:
        return {"error": f"Failed to get lineage graph: {str(e)}"}


@mcp.tool
def get_data_product_usage(data_product_id: str, day_range: int = 30) -> Dict[str, Any]:
    """
    Get cost breakdown and consumer query stats for a data product over a configurable
    time window. Use this to answer questions like 'what did X cost last month?' or
    'which teams query this data product most?'.

    Cost is broken down per output port. Consumer query stats are also per output port,
    with a ranked list of consumer data products by total query count.

    Args:
        data_product_id: UUID obtained from search_data_products or get_data_product_details.
        day_range: Number of days to look back (default 30).
    """
    try:
        if day_range <= 0:
            return {"error": "day_range must be a positive integer"}
        db = next(get_db_session())
        user = get_current_mcp_user()
        try:
            data_product = DataProductService(db).get_data_product(
                id=UUID(data_product_id)
            )
            if not data_product:
                return {"error": f"Data product {data_product_id} not found"}

            # Cost summary aggregated across all output ports
            cost_rows = OutputPortCostService(db).get_data_product_cost_summary(
                UUID(data_product_id), day_range
            )
            cost_by_port = []
            total_cost = Decimal(0)
            for row in cost_rows:
                row_total = (
                    row.compute_cost + row.storage_cost + row.platform_overhead_cost
                )
                total_cost += row_total
                cost_by_port.append(
                    {
                        "output_port_id": str(row.output_port_id),
                        "output_port_name": row.output_port_name,
                        "compute_cost": float(row.compute_cost),
                        "storage_cost": float(row.storage_cost),
                        "platform_overhead_cost": float(row.platform_overhead_cost),
                        "total_cost": float(row_total),
                    }
                )

            # Per-output-port consumer query stats
            output_ports = OutputPortService(db).get_output_ports(
                user=user, data_product_id=UUID(data_product_id)
            )
            consumer_query_stats = []
            for op in output_ports:
                stats_response = OutputPortStatsService(db).get_query_stats(
                    dataset_id=op.id,
                    granularity=QueryStatsGranularity.DAY,
                    day_range=day_range,
                )
                OTHER_CONSUMER_ID = "00000000-0000-0000-0000-000000000000"
                consumer_totals: Dict[str, Any] = {}
                for stat in stats_response.output_port_query_stats_responses:
                    consumer_id = str(stat.consumer_data_product_id)
                    if consumer_id == OTHER_CONSUMER_ID:
                        continue
                    if consumer_id not in consumer_totals:
                        consumer_totals[consumer_id] = {
                            "consumer_data_product_id": consumer_id,
                            "consumer_data_product_name": stat.consumer_data_product_name
                            or "",
                            "total_queries": 0,
                        }
                    consumer_totals[consumer_id]["total_queries"] += stat.query_count

                top_consumers = sorted(
                    consumer_totals.values(),
                    key=lambda c: c["total_queries"],
                    reverse=True,
                )
                consumer_query_stats.append(
                    {
                        "output_port_id": str(op.id),
                        "output_port_name": op.name,
                        "top_consumers": top_consumers,
                    }
                )

            return {
                "data_product_id": data_product_id,
                "day_range": day_range,
                "cost_summary": {
                    "total_cost": float(total_cost),
                    "by_output_port": cost_by_port,
                },
                "consumer_query_stats": consumer_query_stats,
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get data product usage: {str(e)}"}


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
        finally:
            db.close()

    except Exception as e:
        return f"Error retrieving data product resource: {str(e)}"


@mcp.resource("output-port://{output_port_id}")
def get_output_port_resource(output_port_id: str) -> str:
    """Get output port as a resource."""
    try:
        db = next(get_db_session())
        user = get_current_mcp_user()
        try:
            dataset = OutputPortService(db).get_dataset(
                id=UUID(output_port_id), user=user
            )

            if not dataset:
                return f"Error: Output port {output_port_id} not found"
            # Convert to Pydantic model and then to formatted string
            ds_data = GetOutputPortResponse.model_validate(dataset)

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

    except Exception as e:
        return f"Error retrieving marketplace overview: {str(e)}"


@mcp.resource("portal://ontology")
def get_ontology_resource() -> str:
    """Entity model and relationship graph for the Data Product Portal.

    Read this when you need to understand how entities relate, where UUIDs come from,
    or which tool to call to resolve a given entity type.
    """
    return """
## Entity Model

### Domain
- Contains: Data Products
- ID from: get_marketplace_overview() → domains[].id
- Resolved by: get_domain_details(domain_id)

### Data Product
- Belongs to: one Domain
- Exposes: Output Ports, Technical Assets
- Consumes via Input Ports: Output Ports from other Data Products
- ID from: search_data_products(), search_output_ports() → data_product_id,
           get_lineage_graph() → nodes where type=dataProductNode
- Resolved by: get_data_product_details(id), get_data_product_analytics(id)

### Output Port
- Belongs to: one Data Product
- Consumed by: Data Products (via Input Ports, with PENDING/APPROVED/DENIED status)
- Has: table schemas, semantic models, PII tags, freshness
- ID from: search_output_ports(), get_data_product_analytics() → analytics.output_ports[].id,
           get_lineage_graph() → nodes where type=datasetNode
- Resolved by: get_output_port_details(id), get_output_port_model(id)

### Technical Asset
- Belongs to: one Data Product
- ID from: get_data_product_analytics() → analytics.technical_assets[].id
- Resolved by: get_technical_asset_details(id)

### Input Port (access link, not directly addressable by ID)
- Connects: consuming Data Product → Output Port it requests access to
- Status: PENDING | APPROVED | DENIED
- Has: justification, requestor/approver emails, timestamps
- Found in: get_output_port_details() → consuming_data_products[]
            get_data_product_analytics() → analytics.input_ports[]

## Relationships
Domain -[contains]-> Data Product
Data Product -[exposes]-> Output Port
Data Product -[exposes]-> Technical Asset
Data Product -[consumes via Input Port]-> Output Port
Output Port -[has access grants as]-> Input Port

## Access Flow
To check if Data Product A can use Output Port B:
  get_output_port_details(B) → consuming_data_products[] → filter by consuming_data_product_id == A → check status
"""


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
    try:
        db = next(get_db_session())
        current_user = get_current_mcp_user()

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
    List all users and their roles on a specific data product or output port.

    Args:
        resource_type: Type of resource. Valid values: 'data_product' or 'dataset' (output ports use 'dataset').
        resource_id: UUID of the resource.
        limit: Maximum number of role assignments to return.
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
