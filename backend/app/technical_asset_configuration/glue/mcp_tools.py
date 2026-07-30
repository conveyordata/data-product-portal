"""MCP tools for the Glue/Athena data output configuration plugin.

Registers tools that allow AI clients to query AWS Glue databases via Athena,
using the credentials obtained through the portal's access control system.
"""

from typing import TYPE_CHECKING, Any, Dict
from uuid import UUID

import boto3
from fastmcp import FastMCP
from fastmcp.dependencies import Depends
from sqlalchemy import select as sa_select
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    EnvironmentConfigsGetItem,
)
from app.configuration.environments.platform_service_configurations.schemas import (
    AWSGlueConfig,
)
from app.configuration.environments.service import EnvironmentService
from app.core.auth.credentials import AWSCredentials
from app.core.auth.service import AuthService
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.technical_assets.model import ensure_technical_asset_exists
from app.data_products.technical_assets.schema_response import compute_technical_info
from app.data_products.technical_assets.service import DataOutputService
from app.mcp.deps import (
    authorize_data_product_read_integrations,
    get_db_session,
    get_mcp_authenticated_user,
)
from app.settings import settings
from app.technical_asset_configuration.glue.model import (
    GlueTechnicalAssetConfiguration as GlueTechnicalAssetConfigurationModel,
)
from app.technical_asset_configuration.glue.schema import (
    GlueTechnicalAssetConfiguration,
)
from app.users.schema import User

if TYPE_CHECKING:
    from app.technical_asset_configuration.schema_union import DataOutputConfiguration


def _fetch_aws_credentials(
    data_product_namespace: str,
    env: str,
    authorized_user: User,
    db: Session,
) -> AWSCredentials:
    """Fetch temporary AWS credentials for the authenticated user.

    Validates READ_INTEGRATIONS authorization via Casbin, then assumes the IAM
    role to get temporary credentials.
    """
    authorize_data_product_read_integrations(
        data_product_namespace=data_product_namespace,
        authorized_user=authorized_user,
        db=db,
    )

    envs = EnvironmentService(db).get_environments()
    if env not in [e.name for e in envs]:
        raise ValueError(
            f"Environment '{env}' not found. "
            f"Available environments: {[e.name for e in envs]}"
        )
    creds = AuthService().get_aws_credentials(
        data_product_name=data_product_namespace,
        environment=env,
        authorized_user=authorized_user,
        db=db,
    )

    if not isinstance(creds, AWSCredentials):
        raise TypeError("Invalid credentials format")
    return creds


MCP_INSTRUCTIONS = """
    ═══════════════════════════════════════════════════════════════════════
    DATA QUERY FLOW (Glue / Athena — Steps 4–8)
    ═══════════════════════════════════════════════════════════════════════

    Step 4: CHECK ACCESS — TRY CONSUMING DATA PRODUCTS FIRST 🔑
    ────────────────────────────────────────────────────────────
    get_aws_credentials(namespace, environment)
    Try consuming data product namespaces first, then the owner namespace.
    Use the same namespace for ALL subsequent calls.

    Step 5: GET DATABASE + BUCKET + WORKGROUP
    ────────────────────────────────────────────
    get_glue_database(environment, technical_asset_id, data_product_namespace)
    → Returns {'database': '...', 'bucket': '...', 'workgroup': '...'}
    → Resolves database name from owner's technical asset (always correct)
    → Resolves workgroup for the CONSUMING data product (data_product_namespace param)
    → Use database directly in SQL queries — no prefix computation needed.
    → Pass bucket and workgroup to query_athena (both optional).

    CRITICAL: Pass data_product_namespace (consuming product) to get the correct workgroup!
    The workgroup template is rendered for the consumer's namespace, allowing them to
    query using their own IAM role and workgroup permissions.

    Step 6: LIST TABLES
    ────────────────────
    list_glue_tables(data_product_namespace, environment, database_name)

    Step 7: EXECUTE QUERY
    ──────────────────────
    query_athena(data_product_namespace, env, query, bucket=None, workgroup=None)
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


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def get_aws_credentials(
        data_product_namespace: str,
        env: str,
        authorized_user: User = Depends(get_mcp_authenticated_user),
        db: Session = Depends(get_db_session),
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
        creds = _fetch_aws_credentials(data_product_namespace, env, authorized_user, db)
        return {
            "AccessKeyId": creds.AccessKeyId,
            "SecretAccessKey": creds.SecretAccessKey,
            "SessionToken": creds.SessionToken,
        }

    @mcp.tool
    def get_glue_database(
        environment: str,
        technical_asset_id: str,
        data_product_namespace: str = "",
        db: Session = Depends(get_db_session),
    ) -> Dict[str, str]:
        """Get the Athena database name and S3 results bucket for a technical asset.

        Args:
            environment: The environment name (e.g. 'prod', 'dev').
            technical_asset_id: UUID of the Glue technical asset (owner's asset).
            data_product_namespace: (Optional) Consuming data product namespace for workgroup resolution.
                If provided, the workgroup is rendered for the consumer's namespace, allowing them to
                query using their own IAM role and workgroup. If empty, defaults to the owner's namespace.
        Returns:
            {'database': '<fully-qualified db name>', 'bucket': '<s3 bucket name>', 'workgroup': '<workgroup name>'}
            or {'error': '...'} on failure.
        """
        asset_uuid = UUID(technical_asset_id)
        do = ensure_technical_asset_exists(asset_uuid, db=db)
        data_output = DataOutputService(db).get_data_output(do.owner_id, id=asset_uuid)

        configuration: DataOutputConfiguration = data_output.configuration  # type: ignore[assignment]
        if not isinstance(configuration, GlueTechnicalAssetConfigurationModel):
            return {
                "error": f"Technical asset {technical_asset_id} is not a Glue asset"
            }

        data_product = db.scalar(
            sa_select(DataProductModel).where(
                DataProductModel.id == data_output.owner_id
            )
        )
        owner_namespace = data_product.namespace if data_product else ""

        # Use consuming data product namespace for workgroup if provided, otherwise use owner's
        workgroup_namespace = data_product_namespace or owner_namespace

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
            tech_infos = compute_technical_info(
                config_schema, data_output.service, [env_config]
            )
            if not tech_infos or not tech_infos[0].info:
                return {
                    "error": f"No Glue info rendered for environment '{environment}'"
                }
            database = tech_infos[0].info.split(".")[0]
            glue_config = config_schema.get_configuration(env_config.config)

            # athena_workgroup_template is a service-level setting — the same value
            # appears on every entry. Fall back to the first available Glue config
            # if there is no entry whose identifier matches the technical asset's
            # database field (e.g. demo / sample data scenarios).
            any_glue_config = glue_config or next(
                (c for c in env_config.config if isinstance(c, AWSGlueConfig)), None
            )
            workgroup_template = (
                any_glue_config.athena_workgroup_template if any_glue_config else ""
            )
            workgroup = (
                config_schema.render_template(
                    workgroup_template,
                    data_product_namespace=workgroup_namespace,
                    environment=environment,
                    environment_acronym=env_config.environment.acronym,
                )
                if workgroup_template
                else ""
            )
            return {
                "database": database,
                "workgroup": workgroup,
            }

        return {
            "error": f"Environment '{environment}' not found for this technical asset"
        }

    @mcp.tool
    def list_glue_tables(
        data_product_namespace: str,
        env: str,
        database_name: str,
        authorized_user: User = Depends(get_mcp_authenticated_user),
        db: Session = Depends(get_db_session),
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
        creds = _fetch_aws_credentials(data_product_namespace, env, authorized_user, db)
        client = boto3.client(
            "glue",
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=creds.AccessKeyId,
            aws_secret_access_key=creds.SecretAccessKey,
            aws_session_token=creds.SessionToken,
        )
        paginator = client.get_paginator("get_tables")
        tables: list[dict] = [
            {
                "name": t["Name"],
                "database": database_name,
                "full_name": f"{database_name}.{t['Name']}",
                "description": t.get("Description", ""),
                "table_type": t.get("TableType", ""),
                "created_at": str(t.get("CreateTime", "")),
                "updated_at": str(t.get("UpdateTime", "")),
            }
            for page in paginator.paginate(DatabaseName=database_name)
            for t in page.get("TableList", [])
        ]
        return {
            "database": database_name,
            "data_product_namespace": data_product_namespace,
            "environment": env,
            "tables": tables,
            "table_count": len(tables),
            "table_names": [t["name"] for t in tables],
        }

    @mcp.tool
    def query_athena(
        data_product_namespace: str,
        env: str,
        query: str,
        bucket: str = "",
        workgroup: str = "",
        authorized_user: User = Depends(get_mcp_authenticated_user),
        db: Session = Depends(get_db_session),
    ) -> Dict[str, Any]:
        """Run an Athena query using temporary credentials for a data product and environment.

        Use the database name returned by get_glue_database directly in the SQL.
        Pass the bucket and workgroup from get_glue_database if available.

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
            workgroup: Athena workgroup (from get_glue_database). Falls back to server default if absent.
        Returns:
            {'query_execution_id': '...', ...} or {'error': '...'}.
        """
        creds = _fetch_aws_credentials(data_product_namespace, env, authorized_user, db)
        client = boto3.client(
            "athena",
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=creds.AccessKeyId,
            aws_secret_access_key=creds.SecretAccessKey,
            aws_session_token=creds.SessionToken,
        )
        kwargs: Dict[str, Any] = {"QueryString": query}
        if workgroup:
            kwargs["WorkGroup"] = workgroup
        if bucket:
            kwargs["ResultConfiguration"] = {
                "OutputLocation": f"s3://{bucket}/athena-results"
            }
        response = client.start_query_execution(**kwargs)
        result = {
            "query_execution_id": response["QueryExecutionId"],
            "data_product_namespace": data_product_namespace,
            "environment": env,
            "query": query,
            "status": "Query submitted. Use get_athena_query_results to poll for results.",
        }
        if workgroup:
            result["workgroup"] = workgroup
        if bucket:
            result["output_location"] = f"s3://{bucket}/athena-results"
        return result

    @mcp.tool
    def get_athena_query_results(
        query_execution_id: str,
        data_product_namespace: str,
        env: str,
        max_results: int = 100,
        authorized_user: User = Depends(get_mcp_authenticated_user),
        db: Session = Depends(get_db_session),
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
        creds = _fetch_aws_credentials(data_product_namespace, env, authorized_user, db)
        client = boto3.client(
            "athena",
            region_name=settings.AWS_DEFAULT_REGION,
            aws_access_key_id=creds.AccessKeyId,
            aws_secret_access_key=creds.SecretAccessKey,
            aws_session_token=creds.SessionToken,
        )
        execution = client.get_query_execution(QueryExecutionId=query_execution_id)
        exec_status = execution["QueryExecution"]["Status"]["State"]
        stats = execution["QueryExecution"]["Statistics"]

        result: Dict[str, Any] = {
            "query_execution_id": query_execution_id,
            "status": exec_status,
            "data_scanned_bytes": stats.get("DataScannedInBytes", 0),
            "execution_time_ms": stats.get("EngineExecutionTimeInMillis", 0),
        }

        if exec_status == "FAILED":
            raise RuntimeError(
                execution["QueryExecution"]["Status"].get(
                    "StateChangeReason", "Query failed"
                )
            )

        if exec_status in ("QUEUED", "RUNNING"):
            result["message"] = f"Query is {exec_status.lower()}. Retry in a moment."
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
