"""MCP tools for the Glue/Athena data output configuration plugin.

Registers tools that allow AI clients to query AWS Glue databases via Athena,
using the credentials obtained through the portal's access control system.
"""

from typing import TYPE_CHECKING, Any, Dict
from uuid import UUID

import boto3
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from fastmcp.server.dependencies import AccessToken, get_access_token
from sdk.api_client.api.authentication import (
    get_aws_credentials as sdk_get_aws_credentials,
)
from sdk.api_client.client import AuthenticatedClient
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGetItem,
)
from app.configuration.environments.platform_service_configurations.schemas import (
    AWSS3Config,
)
from app.configuration.environments.service import EnvironmentService
from app.core.auth.auth import get_authenticated_user
from app.core.auth.jwt import JWTToken
from app.data_products.technical_assets.model import ensure_technical_asset_exists
from app.data_products.technical_assets.schema_response import compute_technical_info
from app.data_products.technical_assets.service import DataOutputService
from app.database.database import SessionLocal
from app.mcp.deps import get_db_session
from app.mcp.plugin_registry import MCPPlugin
from app.settings import settings
from app.technical_asset_configuration.glue.model import (
    GlueTechnicalAssetConfiguration as GlueTechnicalAssetConfigurationModel,
)
from app.technical_asset_configuration.glue.schema import (
    GlueTechnicalAssetConfiguration,
)

if TYPE_CHECKING:
    from app.technical_asset_configuration.schema_union import DataOutputConfiguration


def _fetch_aws_credentials(data_product_namespace: str, env: str) -> dict[str, str]:
    """Fetch temporary AWS credentials via the portal SDK.

    Validates that the current MCP user has access to the given data product.
    Returns AccessKeyId / SecretAccessKey / SessionToken on success,
    or {'error': '...'} on failure.
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
                "error": (
                    f"Environment '{env}' not found. "
                    f"Available environments: {[e.name for e in envs]}"
                )
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


class GlueMCPPlugin(MCPPlugin):
    """MCP plugin for AWS Glue / Athena data access."""

    @property
    def instructions(self) -> str:
        return """
    ═══════════════════════════════════════════════════════════════════════
    DATA QUERY FLOW (Glue / Athena — Steps 4–8)
    ═══════════════════════════════════════════════════════════════════════

    Step 4: CHECK ACCESS — TRY CONSUMING DATA PRODUCTS FIRST 🔑
    ────────────────────────────────────────────────────────────
    get_aws_credentials(namespace, environment)
    Try consuming data product namespaces first, then the owner namespace.
    Use the same namespace for ALL subsequent calls.

    Step 5: GET DATABASE + BUCKET
    ────────────────────────────────
    get_glue_database(environment, technical_asset_id)
    → Returns {'database': '...', 'bucket': '...'}
    → Use database directly in SQL queries — no prefix computation needed.
    → Pass bucket to query_athena (optional — workgroup default used if absent).

    Step 6: LIST TABLES
    ────────────────────
    list_glue_tables(data_product_namespace, environment, database_name)

    Step 7: EXECUTE QUERY
    ──────────────────────
    query_athena(data_product_namespace, env, query, bucket=None)
    → Use the database name from get_glue_database directly in the SQL:
      SELECT * FROM "datalake_prod_my-product__sales"."users"
    → Always quote names that contain hyphens.

    Step 8: GET RESULTS
    ────────────────────
    get_athena_query_results(query_execution_id, data_product_namespace, env)
    → RUNNING → wait 3-5 s and retry
    → SUCCEEDED → return formatted rows
    → FAILED    → show error
"""

    def register_tools(self, mcp: FastMCP) -> None:
        @mcp.tool
        def get_aws_credentials(
            data_product_namespace: str, env: str
        ) -> Dict[str, str]:
            """Get temporary AWS credentials for a specific data product and environment.

            Validates that the authenticated user has access to the data product.

            WORKFLOW: Try credentials in this order:
            1. FIRST: Each consuming data product namespace from data_product_links[]
            2. LAST:  The owner data product namespace (fallback only)

            The namespace that successfully returns credentials MUST be used for ALL
            subsequent tool calls (query_athena, list_glue_tables, etc.).

            Args:
                data_product_namespace: The namespace to try.
                env: The environment name (full name, no abbreviations).
            Returns:
                AccessKeyId / SecretAccessKey / SessionToken, or {'error': '...'}.
            """
            return _fetch_aws_credentials(data_product_namespace, env)

        @mcp.tool
        def get_glue_database(
            environment: str,
            technical_asset_id: str,
            db: Session = Depends(get_db_session),
        ) -> Dict[str, str]:
            """Get the Athena database name and S3 results bucket for a technical asset.

            Args:
                environment: The environment name (e.g. 'prod', 'dev').
                technical_asset_id: UUID of the Glue technical asset.
            Returns:
                {'database': '<fully-qualified db name>', 'bucket': '<s3 bucket name>'}
                or {'error': '...'} on failure.
            """
            asset_uuid = UUID(technical_asset_id)
            do = ensure_technical_asset_exists(asset_uuid, db=db)
            data_output = DataOutputService(db).get_data_output(
                do.owner_id, id=asset_uuid
            )

            configuration: DataOutputConfiguration = data_output.configuration  # type: ignore[assignment]
            if not isinstance(configuration, GlueTechnicalAssetConfigurationModel):
                return {
                    "error": f"Technical asset {technical_asset_id} is not a Glue asset"
                }

            config_schema = GlueTechnicalAssetConfiguration.model_validate(
                configuration, from_attributes=True
            )
            env_configs = [
                EnvironmentConfigsGetItem.model_validate(e)
                for e in data_output.environment_configurations
            ]
            for env_config in env_configs:
                if env_config.environment.name.lower() != environment.lower():
                    continue
                glue_config = config_schema.get_configuration(env_config.config)
                if glue_config is None:
                    return {
                        "error": f"No Glue config found for environment '{environment}'"
                    }
                tech_infos = compute_technical_info(
                    config_schema, data_output.service, [env_config]
                )
                if not tech_infos or not tech_infos[0].info:
                    return {
                        "error": f"No Glue info rendered for environment '{environment}'"
                    }
                database = tech_infos[0].info.split(".")[0]
                s3_config = next(
                    (
                        c
                        for c in env_config.config
                        if isinstance(c, AWSS3Config)
                        and c.identifier == glue_config.bucket_identifier
                    ),
                    None,
                )
                return {
                    "database": database,
                    "bucket": s3_config.bucket_name if s3_config else "",
                }

            return {
                "error": f"Environment '{environment}' not found for this technical asset"
            }

        @mcp.tool
        def list_glue_tables(
            data_product_namespace: str, env: str, database_name: str
        ) -> Dict[str, Any]:
            """List all tables in a Glue database for a data product and environment.

            IMPORTANT: Use the SAME data_product_namespace that successfully returned
            credentials in get_aws_credentials(). This is typically a CONSUMING data
            product namespace, not the owner namespace.

            Args:
                data_product_namespace: The namespace with access (from consuming data product).
                env: The environment (e.g. 'prod', 'dev').
                database_name: The Glue database name, possibly including environment prefix.
            Returns:
                List of table names, or error if access denied / database not found.
            """
            creds = _fetch_aws_credentials(data_product_namespace, env)
            if "error" in creds:
                return creds

            try:
                client = boto3.client(
                    "glue",
                    region_name=settings.AWS_DEFAULT_REGION,
                    aws_access_key_id=creds["AccessKeyId"],
                    aws_secret_access_key=creds["SecretAccessKey"],
                    aws_session_token=creds["SessionToken"],
                )
                tables: list[dict] = []
                next_token = None
                while True:
                    params: dict[str, Any] = {"DatabaseName": database_name}
                    if next_token:
                        params["NextToken"] = next_token
                    response = client.get_tables(**params)
                    tables.extend(
                        {
                            "name": t["Name"],
                            "database": database_name,
                            "full_name": f"{database_name}.{t['Name']}",
                            "description": t.get("Description", ""),
                            "table_type": t.get("TableType", ""),
                            "created_at": str(t.get("CreateTime", "")),
                            "updated_at": str(t.get("UpdateTime", "")),
                        }
                        for t in response.get("TableList", [])
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
                    "error": f"Failed to list Glue tables: {e}",
                    "database": database_name,
                    "data_product_namespace": data_product_namespace,
                    "environment": env,
                }

        @mcp.tool
        def query_athena(
            data_product_namespace: str,
            env: str,
            query: str,
            bucket: str = "",
        ) -> Dict[str, Any]:
            """Run an Athena query using temporary credentials for a data product and environment.

            Use the database name returned by get_glue_database directly in the SQL.
            Pass the bucket from get_glue_database if available; omit to use the
            workgroup's configured default output location.

            CRITICAL: Use the SAME data_product_namespace that worked in get_aws_credentials().

            SQL SYNTAX:
            - Use the full database name from get_glue_database in every query
            - Quote names that contain hyphens or special characters:
              ✓ SELECT * FROM "datalake_prod_sales-data__sales"."users"
              ✗ SELECT * FROM users

            Args:
                data_product_namespace: The namespace with access (consuming data product).
                env: The environment.
                query: SQL query to execute.
                bucket: S3 bucket for results (from get_glue_database). Optional.
            Returns:
                {'query_execution_id': '...', ...} or {'error': '...'}.
            """
            creds = _fetch_aws_credentials(data_product_namespace, env)
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
                workgroup = (
                    f"{settings.AWS_ATHENA_PREFIX}-{data_product_namespace}-{env}"
                )
                kwargs: Dict[str, Any] = {
                    "QueryString": query,
                    "WorkGroup": workgroup,
                }
                if bucket:
                    kwargs["ResultConfiguration"] = {
                        "OutputLocation": f"s3://{bucket}/athena-results"
                    }
                response = client.start_query_execution(**kwargs)
                result = {
                    "query_execution_id": response["QueryExecutionId"],
                    "data_product_namespace": data_product_namespace,
                    "environment": env,
                    "workgroup": workgroup,
                    "query": query,
                    "status": "Query submitted. Use get_athena_query_results to poll for results.",
                }
                if bucket:
                    result["output_location"] = f"s3://{bucket}/athena-results"
                return result
            except client.exceptions.InvalidRequestException as e:
                return {"error": f"Invalid Athena query: {e}", "query": query}
            except Exception as e:
                return {"error": f"Failed to execute Athena query: {e}", "query": query}

        @mcp.tool
        def get_athena_query_results(
            query_execution_id: str,
            data_product_namespace: str,
            env: str,
            max_results: int = 100,
        ) -> Dict[str, Any]:
            """Get the status and results of a previously submitted Athena query.

            Args:
                query_execution_id: The ID returned by query_athena.
                data_product_namespace: The namespace used when submitting the query.
                env: The environment.
                max_results: Maximum rows to return (default 100).
            Returns:
                Status and result rows, or error information.
            """
            creds = _fetch_aws_credentials(data_product_namespace, env)
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
                execution = client.get_query_execution(
                    QueryExecutionId=query_execution_id
                )
                exec_status = execution["QueryExecution"]["Status"]["State"]
                stats = execution["QueryExecution"]["Statistics"]

                result: Dict[str, Any] = {
                    "query_execution_id": query_execution_id,
                    "status": exec_status,
                    "data_scanned_bytes": stats.get("DataScannedInBytes", 0),
                    "execution_time_ms": stats.get("EngineExecutionTimeInMillis", 0),
                }

                if exec_status == "FAILED":
                    result["error"] = execution["QueryExecution"]["Status"].get(
                        "StateChangeReason", "Query failed"
                    )
                    return result

                if exec_status in ("QUEUED", "RUNNING"):
                    result["message"] = (
                        f"Query is {exec_status.lower()}. Retry in a moment."
                    )
                    return result

                if exec_status == "SUCCEEDED":
                    rows_response = client.get_query_results(
                        QueryExecutionId=query_execution_id, MaxResults=max_results
                    )
                    rows = rows_response["ResultSet"]["Rows"]
                    if not rows:
                        result.update({"rows": [], "row_count": 0})
                        return result

                    headers = [col.get("VarCharValue", "") for col in rows[0]["Data"]]
                    data_rows = [
                        {
                            headers[i]: col.get("VarCharValue")
                            for i, col in enumerate(row["Data"])
                        }
                        for row in rows[1:]
                    ]
                    result.update(
                        {
                            "columns": headers,
                            "rows": data_rows,
                            "row_count": len(data_rows),
                            "truncated": len(data_rows) >= max_results,
                        }
                    )
                    return result

                result["message"] = f"Unexpected query status: {exec_status}"
                return result

            except Exception as e:
                return {
                    "error": f"Failed to get query results: {e}",
                    "query_execution_id": query_execution_id,
                }
