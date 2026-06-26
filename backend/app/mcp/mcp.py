from contextlib import asynccontextmanager
from typing import Any, Dict, Optional, Sequence
from uuid import UUID

import boto3
import jwt as pyjwt
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.dependencies import AccessToken, get_access_token
from sdk.api_client.api.authentication import (
    get_aws_credentials as sdk_get_aws_credentials,
)
from sdk.api_client.client import AuthenticatedClient
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
from app.configuration.environments.platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration as EnvPlatformServiceConfigurationModel,
)
from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGetItem,
)
from app.configuration.environments.schema_response import EnvironmentGetItem
from app.configuration.environments.service import EnvironmentService
from app.configuration.platforms.model import Platform
from app.configuration.platforms.platform_services.model import PlatformService
from app.core.auth.auth import get_authenticated_user
from app.core.auth.jwt import JWTToken, get_oidc
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
            base_url=f"{(settings.MCP_BASE_URL or settings.HOST).rstrip('/')}/mcp",
            require_authorization_consent="external",
            allowed_client_redirect_uris=settings.MCP_AUTH_REDIRECT_URIS,
        )
    logger.debug("[MCP] OIDC disabled — MCP server will run without authentication")
    return None


mcp = FastMCP(
    name="DataProductPortalMCP",
    instructions="""
    Portal for discovering and exploring data products and output ports.

    CORE CONCEPTS:
    - Output ports (datasets) = published, queryable datasets
    - Data products = containers grouping related output ports and infrastructure
    - Technical assets = underlying infrastructure (e.g., Glue databases)
    - Environments = deployment stages (prod, staging, dev)

    ═══════════════════════════════════════════════════════════════════════
    TWO DISTINCT MODES OF OPERATION
    ═══════════════════════════════════════════════════════════════════════

    MODE 1: DISCOVERY (Metadata Only - Fast, No Credentials Required)
    ──────────────────────────────────────────────────────────────────────
    Use this when the user wants to:
    - Find what data exists: "What sales datasets are available?"
    - Get metadata: "Who owns the customer data?", "What's in the sales_db?"
    - Explore the catalog: "Show me all data products in the finance domain"
    - Check ownership/descriptions: "What does the revenue_monthly table contain?"

    Tools for Discovery (no credentials needed):
    - search_output_ports(query) - find datasets
    - search_data_products(query) - find data products
    - get_output_port_details(id) - metadata about a dataset
    - get_data_product_details(id) - details about a data product
    - get_data_product_analytics(id) - what output ports a data product has
    - get_marketplace_overview() - high-level statistics
    - get_environments() - available environments

    MODE 2: DATA QUERIES (Actual Data - Requires AWS Credentials)
    ──────────────────────────────────────────────────────────────────────
    Use this when the user wants to:
    - See actual data: "Show me sales from last month"
    - Run analytics: "What are the top 10 customers by revenue?"
    - Query tables: "SELECT * FROM sales_db.transactions WHERE date > '2026-01-01'"
    - Get row-level data: "How many orders were placed yesterday?"
    - Find records in data: "Which users are in the sales data?"

    ═══════════════════════════════════════════════════════════════════════
    DATA QUERY FLOW (Step-by-Step)
    ═══════════════════════════════════════════════════════════════════════

    🔑 CRITICAL: Most data access happens through CONSUMING data products, not
    direct ownership. Always check data_product_links in output port details!

    Step 1: DISCOVER THE DATA
    ──────────────────────────
    search_output_ports("user's query")
    → Returns: output ports with IDs, names, descriptions, data_product_id
    → Action: Pick the most relevant output port

    Step 2: GET METADATA & CONSUMING DATA PRODUCTS 🔑
    ────────────────────────────────────────────────────
    get_output_port_details(output_port_id)
    → Returns: namespace, database name, technical_asset_links, data_product_links
    → IMPORTANT: data_product_links contains consuming data products that can access this data
    → Action: Extract BOTH:
      1. The owner data_product_id (for direct access attempt)
      2. ALL data_product_links[].data_product.namespace (for fallback access)

    If you don't have the consuming products there is a specific tool for that as well:
    get_consuming_products(output_port_id, data_product_id) where data_product_id is the owner data product of the output port. This will return a list of consuming products with their namespaces and descriptions.

    Step 3: DETERMINE ENVIRONMENT
    ──────────────────────────────
    If user didn't specify environment:
    • get_environments()
    • Use default or ask user
    → Action: Decide which environment to query

    Step 4: CHECK ACCESS - TRY CONSUMING DATA PRODUCTS FIRST 🔑
    ────────────────────────────────────────────────────────────
    IMPORTANT: Users typically access data through CONSUMING data products,
    not by owning the source data product. Always try consuming products first!

    From Step 2, you have data_product_links[] from the output port.

    WORKFLOW:
    A. For EACH data_product in data_product_links:
       1. Extract: namespace = data_product.namespace
       2. Try: get_aws_credentials(namespace, environment)
       3. If SUCCESS → Use this namespace for ALL subsequent queries (Step 5+)
       4. If FAILED → Try next consuming product

    B. If ALL consuming products fail, try the owner data product:
       get_aws_credentials(owner_namespace, environment)

    C. If EVERYTHING fails → Tell user:
       "No access to this data. Request access from [owner] or these
        consuming data products: [list names from data_product_links]"

    ⚠️  REMEMBER: Once you find working credentials, use that SAME namespace
        for query_athena in the following steps!

    Step 5: FIND DATABASE
    ──────────────────────────────
    Defer the database name from the technical asset or query athena to find it.
    Use get_glue_database(environment, technical_asset_id) tool

    Step 6: LIST AVAILABLE TABLES
     ──────────────────────────────
    list_glue_tables(data_product_namespace, environment, database_name)
    → Use the SAME data_product_namespace that worked in Step 4!
    → database_name may need environment prefix (e.g., 'datalake_experimentation_')
    → database may need suffixes found in technical asset links (e.g., __sales)
    → Returns: list of table names in the database
    → Action: Identify which table(s) to query

    Step 7: CONSTRUCT & EXECUTE QUERY
    ──────────────────────────────────
    query_athena(
        data_product_namespace,  # SAME namespace from Step 4!
        environment,
        "SELECT * FROM database_name.table_name WHERE ..."
    )
    → Returns: query_execution_id
    → CRITICAL: Use fully qualified names with quotes for hyphens:
      ✓ CORRECT: SELECT * FROM "datalake_experimentation_sales-data__sales"."users"
      ✗ WRONG:   SELECT * FROM users (missing database)
      ✗ WRONG:   SELECT * FROM datalake_experimentation_sales-data__sales.users (no quotes)

    Step 8: GET RESULTS
    ───────────────────
    get_athena_query_results(query_execution_id, data_product_namespace, environment)
    → If status = 'RUNNING': Wait 3-5 seconds, retry
    → If status = 'SUCCEEDED': Return formatted results to user
    → If status = 'FAILED': Show error message

    ═══════════════════════════════════════════════════════════════════════
    EXAMPLES
    ═══════════════════════════════════════════════════════════════════════

    EXAMPLE 1: Discovery (Metadata)
    ───────────────────────────────
    User: "What sales datasets do we have?"

    1. search_output_ports("sales")
       → Returns: [sales_monthly, sales_transactions, sales_regions]
    2. Present to user:
       "We have 3 sales datasets:
        • sales_monthly - Monthly aggregated sales data
        • sales_transactions - Raw transaction data
        • sales_regions - Sales by geographic region"

    EXAMPLE 2: Data Query (Success)
    ────────────────────────────────
    User: "Show me top 10 customers by revenue"

    1. search_output_ports("customer revenue")
       → Found: output_port_id=abc-123, data_product_id=xyz-789
    2. get_output_port_details("abc-123")
       → namespace="sales_data", database="sales_db"
    3. get_environments() → ['prod', 'staging', 'dev']
       → Use: 'prod' (default)
    4. get_aws_credentials("sales_data", "prod")
       → ✓ Success: got credentials
    6. query_athena("sales_data", "prod",
         "SELECT customer_name, revenue FROM sales_db.customer_revenue
          ORDER BY revenue DESC LIMIT 10")
       → execution_id="qry-456"
    7. get_athena_query_results("qry-456", "sales_data", "prod")
       → Returns: [{customer_name: "Acme Corp", revenue: 1000000}, ...]

    EXAMPLE 3: Data Query via Consuming Product (MOST COMMON CASE)
    ────────────────────────────────────────────────────────────────
    User: "Which users are in the sales data?"

    1. search_output_ports("sales") → Found: output_port_id=abc-123
    2. get_output_port_details("abc-123")
       → owner namespace="mcp-athena-query-test"
       → database="mcp-athena-query-test"
       → data_product_links: [{data_product: {namespace: "mcp-test-sales-overview"}}]
    3. get_environments() → Use 'dev'
    4. Try consuming product FIRST:
       get_aws_credentials("mcp-test-sales-overview", "dev")
       → ✓ Success! Use this namespace for all queries
    6. query_athena("mcp-test-sales-overview", "dev",
         'SELECT * FROM "datalake_experimentation_mcp-athena-query-test__sales"."users" LIMIT 100')
       → Note: Quotes around database/table names with hyphens!
    7. get_athena_query_results(...) → Returns user data

    ═══════════════════════════════════════════════════════════════════════
    IMPORTANT RULES
    ═══════════════════════════════════════════════════════════════════════

    ✓ DO:
    - Route to Discovery mode for metadata questions (no credentials needed)
    - Route to Query mode for actual data questions (credentials required)
    - ALWAYS extract data_product_links from output port details
    - TRY CONSUMING DATA PRODUCTS FIRST - this is the most common access pattern
    - Use the SAME namespace for query_athena that worked in get_aws_credentials
    - Use fully qualified table names with quotes: "database"."table_name"
    - Be aware of environment prefixes in database names (e.g., 'datalake_experimentation_')
    - Wait and retry if query is still running
    - Default to 'dev' environment unless specified

    ✗ DON'T:
    - Don't try owner access first - consuming products are the primary access pattern
    - Don't request credentials for pure metadata questions
    - Don't skip extracting data_product_links from output port details
    - Don't skip the get_prefix step - you need actual table names with prefixes
    - Don't use unqualified table names (missing database prefix)
    - Don't forget quotes around database/table names with hyphens or underscores
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


@mcp.tool
def get_aws_credentials(data_product_namespace: str, env: str) -> Dict[str, str]:
    """Get temporary AWS credentials for a specific data product and environment.
    This validates that the authenticated user has access to the data product.
    If the user doesn't have access, the CLI command will fail.

    WORKFLOW: When querying data from an output port, try credentials in this order:
    1. FIRST: Try each consuming data product namespace from data_product_links[]
    2. LAST: Try the owner data product namespace (fallback only)

    ALWAYS use full names for environments. Never abbreviations

    The namespace that successfully returns credentials should be used for ALL
    subsequent operations (query_athena, get_athena_query_results).

    Args:
        data_product_namespace: The namespace to try (consuming product or owner).
        env: The environment to run on.

    Returns:
        AWS credentials including AccessKeyId, SecretAccessKey, and SessionToken.
        Returns error if access is denied or credentials cannot be retrieved.
    """
    db = SessionLocal()
    try:
        access_token: AccessToken = get_access_token()
        get_authenticated_user(
            token=JWTToken(sub="", token=f"Bearer {access_token.token}"),
            db=db,
        )
        envs = EnvironmentService(db).get_environments()
        if env not in [e.name for e in envs]:
            return {
                "error": f"Environment '{env}' not found. Available environments: {[e.name for e in envs]}"
            }
        client = AuthenticatedClient(base_url=settings.HOST, token=access_token.token)
        result = sdk_get_aws_credentials.sync(
            client=client, data_product_name=data_product_namespace, environment=env
        )
        if not result:
            return {
                "error": "You don't have access to this data product or it doesn't exist."
            }
        return {
            "AccessKeyId": result.access_key_id,
            "SecretAccessKey": result.secret_access_key,
            "SessionToken": result.session_token,
        }
    finally:
        db.close()


@mcp.tool
def get_database_prefix(environment: str) -> str:
    prefix = settings.AWS_ATHENA_PREFIX
    return f"{prefix}_{environment}_"


@mcp.tool
def get_glue_database(
    environment: str,
    technical_asset_id: str,
    db: Session = Depends(get_db_session),
) -> str:
    """Get the Glue database name associated with a technical asset.
    This is used to find the database to query in Athena.
    Args:
        environment: The name of the environment to run the query in
        technical_asset_id: The ID of the technical asset to query
    Returns:
        The name of the Glue database to query in Athena.
    """
    technical_asset_uuid = UUID(technical_asset_id)
    do = ensure_technical_asset_exists(technical_asset_uuid, db=db)
    data_output = DataOutputService(db).get_data_output(
        do.owner_id,
        id=technical_asset_uuid,
    )
    technical_asset = GetTechnicalAssetsResponseItem.model_validate(
        data_output
    ).model_dump()
    prefix = settings.AWS_ATHENA_PREFIX
    database = technical_asset.get("configuration", {}).get("database")
    suffix = technical_asset.get("configuration", {}).get("database_suffix")
    return f"{prefix}_{environment}_{database}__{suffix}"


@mcp.tool
def query_athena(
    data_product_namespace: str,
    env: str,
    query: str,
    prefix: str,
    bucket: str,
) -> Dict[str, Any]:
    """Run an Athena query using temporary credentials for a specific data product and environment.
    The prefix and bucket are typically configured at the company level, but can be overridden if needed.
    This tool will automatically check user access by retrieving credentials.

    CRITICAL: Use the SAME data_product_namespace that worked in get_aws_credentials().
    This is typically a CONSUMING data product namespace, not the data owner.

    SQL SYNTAX NOTES:
    - Always use fully qualified names: database.table
    - Use double quotes for names with hyphens or special chars:
      ✓ SELECT * FROM "datalake_experimentation_sales-data__sales"."users"
      ✗ SELECT * FROM datalake_experimentation_sales-data__sales.users (syntax error)
    - Database names often have environment prefixes (<PREFIX>, <PREFIX>)
    e.g. datalake_prd. The prefixes can be found with get_prefix
    - Database names are often suffixed. These suffixes can be found in the technical asset links of the output port details.
    The suffix is always attached with a DOUBLE __ (underscore) e.g. datalake_experimentation_sales-data__sales
    The workgroup must be filled in and is the same namespace as you requested access for.
    Make sure the database exists and is correct before assuming access rights issues are the issue.
    Args:
        data_product_namespace: The namespace that has access (from consuming data product).
        env: The environment.
        query: The SQL query to execute (use quotes for database/table names with hyphens).
        prefix: use get_prefix tool to get database prefixes. Use these in your query.
        bucket: use get_bucket tool to get the correct bucket for the data product and environment, or provide an override.

    Returns:
        Query execution details including QueryExecutionId, or error if query failed.
    """

    # Use company-wide settings as defaults
    results_bucket = bucket

    # Buckets are fetchable from the database I guess?
    # db = next(get_db_session())
    # EnvironmentPlatformServiceConfigurationService(db).get_environment_platform_service_config()

    # Validate that prefix and bucket are available
    if not settings.AWS_ATHENA_PREFIX:
        return {
            "error": "AWS Athena prefix not configured. Please set AWS_ATHENA_PREFIX in settings or provide as parameter."
        }

    if not prefix:
        return {
            "error": "Database prefix not provided. Use get_prefix tool to retrieve the correct prefix for the environment and data product."
        }

    if not results_bucket:
        return {
            "error": "AWS Athena results bucket not configured. Please set AWS_ATHENA_RESULTS_BUCKET in settings or provide as parameter."
        }

    # Get credentials (this also checks access)
    creds = get_aws_credentials(data_product_namespace, env)

    # Check if credential retrieval failed
    if "error" in creds:
        return creds  # Return the error from get_aws_credentials

    try:
        # Create Athena client with temporary credentials
        client = boto3.client(
            "athena",
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

        # Execute the query
        response = client.start_query_execution(
            QueryString=query,
            WorkGroup=f"{settings.AWS_ATHENA_PREFIX}-{data_product_namespace}-{env}",
            ResultConfiguration={
                "OutputLocation": f"s3://{results_bucket}/athena/{data_product_namespace}"
            },
        )
        return {
            "query_execution_id": response["QueryExecutionId"],
            "data_product_namespace": data_product_namespace,
            "environment": env,
            "workgroup": f"{settings.AWS_ATHENA_PREFIX}-{data_product_namespace}-{env}",
            "output_location": f"s3://{results_bucket}/athena/{data_product_namespace}",
            "query": query,
            "status": "Query submitted successfully. Use get_athena_query_results to check status and get results.",
        }

    except client.exceptions.InvalidRequestException as e:
        return {"error": f"Invalid Athena query request: {str(e)}", "query": query}
    except Exception as e:
        return {"error": f"Failed to execute Athena query: {str(e)}", "query": query}


@mcp.tool
def get_athena_query_results(
    query_execution_id: str,
    data_product_namespace: str,
    env: str,
    max_results: int = 100,
) -> Dict[str, Any]:
    """Get the status and results of an Athena query.
    Use this after query_athena to check if the query completed and retrieve results.

    Args:
        query_execution_id: The query execution ID returned from query_athena.
        data_product_namespace: The namespace of the data product.
        env: The environment (e.g., 'prod', 'staging').
        max_results: Maximum number of result rows to return (default 100).

    Returns:
        Query status and results if completed, or status information if still running.
    """
    # Get credentials
    creds = get_aws_credentials(data_product_namespace, env)

    if "error" in creds:
        return creds

    try:
        client = boto3.client(
            "athena",
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

        # Get query execution status
        execution = client.get_query_execution(QueryExecutionId=query_execution_id)
        status = execution["QueryExecution"]["Status"]["State"]

        result = {
            "query_execution_id": query_execution_id,
            "status": status,
            "data_scanned_bytes": execution["QueryExecution"]["Statistics"].get(
                "DataScannedInBytes", 0
            ),
            "execution_time_ms": execution["QueryExecution"]["Statistics"].get(
                "EngineExecutionTimeInMillis", 0
            ),
        }

        # If query failed, include error details
        if status == "FAILED":
            result["error"] = execution["QueryExecution"]["Status"].get(
                "StateChangeReason", "Query failed"
            )
            return result

        # If query is still running
        if status in ["QUEUED", "RUNNING"]:
            result["message"] = (
                f"Query is {status.lower()}. Please try again in a moment."
            )
            return result

        # If query succeeded, get results
        if status == "SUCCEEDED":
            results_response = client.get_query_results(
                QueryExecutionId=query_execution_id, MaxResults=max_results
            )

            # Parse results into a more readable format
            rows = results_response["ResultSet"]["Rows"]
            if not rows:
                result["rows"] = []
                result["row_count"] = 0
                return result

            # First row is headers
            headers = [col.get("VarCharValue", "") for col in rows[0]["Data"]]

            # Remaining rows are data
            data_rows = []
            for row in rows[1:]:
                row_data = {}
                for i, col in enumerate(row["Data"]):
                    row_data[headers[i]] = col.get("VarCharValue", None)
                data_rows.append(row_data)

            result["columns"] = headers
            result["rows"] = data_rows
            result["row_count"] = len(data_rows)
            result["truncated"] = len(data_rows) >= max_results

            return result

        # Unknown status
        result["message"] = f"Unexpected query status: {status}"
        return result

    except Exception as e:
        return {
            "error": f"Failed to get query results: {str(e)}",
            "query_execution_id": query_execution_id,
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
    def _execute(db: Session) -> dict[str, Any]:
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

    try:
        if db is not None:
            return _execute(db)
        session = SessionLocal()
        try:
            return _execute(session)
        finally:
            session.close()
    except Exception as e:
        return {"error": f"Failed to search data products: {str(e)}"}


# Get input port for output ports to figure out consumers
@mcp.tool
def get_consuming_products(output_port_id: str, data_product_id: str) -> Dict[str, Any]:
    """
    Get consuming data products for a specific output port. This is essential for understanding who has access to the data and how users typically access it.

    Args:
        output_port_id: UUID of the output port (dataset) to check.
        data_product_id: UUID of the owning data product of the output port.
    returns:
        List of consuming data products that have access to this output port, including their namespaces and descriptions.
    """
    try:
        db = SessionLocal()
        get_access_token()
        get_mcp_authenticated_user(db=db)
        try:
            consuming_products = OutputPortService(db).get_consuming_data_products(
                UUID(output_port_id), UUID(data_product_id)
            )
            consuming_products_data = [
                {
                    "id": str(input_port.consuming_abstract_data_product.id),
                    "name": input_port.consuming_abstract_data_product.name,
                    "namespace": input_port.consuming_abstract_data_product.namespace,
                    "description": input_port.consuming_abstract_data_product.description,
                }
                for input_port in consuming_products
            ]
            return {
                "output_port_id": output_port_id,
                "consuming_data_products": consuming_products_data,
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get consuming products: {str(e)}"}


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
)
def get_output_port_details(
    output_port_id: str,
    db: Session = Depends(get_db_session),
    user: UserModel = Depends(get_mcp_authenticated_user),
) -> dict[str, Any]:
    dataset = OutputPortService(db).get_visible_dataset(
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


@mcp.tool
def get_bucket(environment_id: str) -> Dict[str, Any]:
    """Get the S3 bucket name configured for Athena query results.
    This is typically set at the company level in settings, but can be useful to confirm before running queries.

    Args:
        environment_id: The environment UUID for which to get the platform service config
    Returns:
        The S3 bucket name for Athena results, or an error if not configured.
    """

    db = SessionLocal()
    try:
        logger.info(f"Getting bucket for environment_id: {environment_id}")

        # Query for AWS S3 configuration by joining with Platform and PlatformService
        stmt = (
            sa_select(EnvPlatformServiceConfigurationModel, Platform, PlatformService)
            .join(
                Platform,
                EnvPlatformServiceConfigurationModel.platform_id == Platform.id,
            )
            .join(
                PlatformService,
                EnvPlatformServiceConfigurationModel.service_id == PlatformService.id,
            )
            .where(
                EnvPlatformServiceConfigurationModel.environment_id
                == UUID(environment_id)
            )
        )

        results = db.execute(stmt).all()
        logger.info(f"Found {len(results)} platform service configs for environment")

        for config_model, platform, service in results:
            logger.info(f"Platform: {platform.name}, Service: {service.name}")
            if platform.name.lower() == "aws" and service.name.lower() == "s3":
                logger.info("Found matching AWS S3 config")

                # Parse the config using the schema
                config_data = EnvironmentConfigsGetItem.model_validate(config_model)
                logger.info(
                    f"Config data parsed, has {len(config_data.config) if config_data.config else 0} configs"
                )

                # Find the default S3 config or use the first one
                s3_config = None
                if config_data.config:
                    s3_config = next(
                        (
                            c
                            for c in config_data.config
                            if hasattr(c, "is_default") and c.is_default
                        ),
                        None,
                    )
                    if not s3_config:
                        s3_config = config_data.config[0]
                    logger.info(f"Selected S3 config: {s3_config}")

                if not s3_config or not hasattr(s3_config, "bucket_name"):
                    logger.error(
                        f"No S3 bucket configured for environment '{environment_id}'."
                    )
                    return {
                        "error": f"No S3 bucket configured for environment '{environment_id}'."
                    }

                logger.info(f"Returning bucket: {s3_config.bucket_name}")
                return {"athena_results_bucket": s3_config.bucket_name}

        return {
            "error": f"AWS S3 configuration not found for environment '{environment_id}'."
        }
    except Exception as e:
        logger.error(f"Error getting bucket: {str(e)}", exc_info=True)
        return {"error": f"Failed to get bucket: {str(e)}"}
    finally:
        db.close()


@mcp.tool
def get_environments() -> Dict[str, Any]:
    """Get the list of available environments (e.g., prod, staging, dev).
    Use this when querying data to determine which environment to access.
    The default environment is typically marked with is_default=True.

    Returns:
        List of environments with their IDs, names, acronyms, and default status.
    """
    try:
        db = SessionLocal()
        try:
            environments = EnvironmentService(db).get_environments()
            serialized_environments = [
                EnvironmentGetItem.model_validate(env).model_dump()
                for env in environments
            ]

            default_env = next((env for env in environments if env.is_default), None)

            return {
                "environments": serialized_environments,
                "count": len(serialized_environments),
                "default_environment": EnvironmentGetItem.model_validate(
                    default_env
                ).model_dump()
                if default_env
                else None,
            }
        finally:
            db.close()

    except Exception as e:
        return {"error": f"Failed to get environments: {str(e)}"}


@mcp.tool
def list_glue_tables(
    data_product_namespace: str, env: str, database_name: str
) -> Dict[str, Any]:
    """List all tables in a Glue database for a specific data product and environment.
    Use this after getting output port details to discover what tables are available to query.
    You must have access to the data product (verify with get_aws_credentials first).

    IMPORTANT: Use the SAME data_product_namespace that successfully returned credentials
    in get_aws_credentials(). This is typically a CONSUMING data product namespace from
    the output port's data_product_links[], NOT the owner namespace.

    NOTE: The database_name often has an environment prefix added by the platform.
    If you get "Database not found", try prefixing or list the available databases.

    Args:
        data_product_namespace: The namespace that has access (from consuming data product).
        env: The environment (e.g., 'prod', 'staging', 'dev').
        database_name: The Glue database name, possibly with environment prefix.

    Returns:
        List of table names in the database, or error if access denied or database not found.
    """
    # Get credentials first to validate access
    creds = get_aws_credentials(data_product_namespace, env)
    if "error" in creds:
        return creds

    try:
        # Create Glue client with temporary credentials
        client = boto3.client(
            "glue",
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

        # List tables in the database
        tables: list[dict] = []
        next_token = None

        while True:
            params = {"DatabaseName": database_name}
            if next_token:
                params["NextToken"] = next_token

            response = client.get_tables(**params)

            # Replace for loop with list.extend
            tables.extend(
                {
                    "name": table["Name"],
                    "database": database_name,
                    "full_name": f"{database_name}.{table['Name']}",
                    "description": table.get("Description", ""),
                    "table_type": table.get("TableType", ""),
                    "created_at": str(table.get("CreateTime", "")),
                    "updated_at": str(table.get("UpdateTime", "")),
                }
                for table in response.get("TableList", [])
            )

            next_token = response.get("NextToken")
            if not next_token:
                break

        return {
            "database": database_name,
            "data_product_namespace": data_product_namespace,
            "environment": env,
            "tables": tables,
            "table_count": len(tables),
            "table_names": [t["name"] for t in tables],
        }

    except client.exceptions.EntityNotFoundException:
        return {
            "error": f"Database '{database_name}' not found in Glue catalog",
            "database": database_name,
            "data_product_namespace": data_product_namespace,
            "environment": env,
        }
    except Exception as e:
        return {
            "error": f"Failed to list Glue tables: {str(e)}",
            "database": database_name,
            "data_product_namespace": data_product_namespace,
            "environment": env,
        }


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
    dataset = OutputPortService(db).get_visible_dataset(
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
