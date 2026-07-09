import logging
import os
import re
from collections.abc import Iterable
from typing import Any
from uuid import UUID

import psycopg2
import yaml


from sdk import AuthenticatedClient, Client, Reconciler
from sdk.api_client.api.configuration_data_product_lifecycles import (
    get_data_products_lifecycles,
)
from sdk.api_client.api.configuration_platforms import (
    get_all_platform_service_configurations,
)
from sdk.api_client.api.data_products import (
    add_data_product_finalizer,
    get_data_product,
    get_data_products,
    remove_data_product_finalizer,
    update_data_product,
    get_data_product_input_ports,
)

from sdk.api_client.api.data_products_technical_assets import (
    create_technical_asset,
    update_technical_asset_status,
    get_data_product_technical_assets,
)
from sdk.api_client.models import (
    AbstractDataProductStatus,
    CreateTechnicalAssetRequest,
    DataOutputStatusUpdate,
    DataProductLifeCyclesGetItem,
    DataProductUpdate,
    FinalizerRequest,
    GetDataProductResponse,
    GetDataProductsResponse,
    HTTPValidationError,
    PlatformServiceConfiguration,
    GetDataProductInputPortsResponse,
    GetTechnicalAssetsResponse,
)
from sdk.api_client.models.access_granularity import AccessGranularity
from sdk.api_client.models.postgre_sql_technical_asset_configuration import (
    PostgreSQLTechnicalAssetConfiguration,
)
from sdk.api_client.models.osi_semantic_model_technical_asset_configuration import (
    OSISemanticModelTechnicalAssetConfiguration,
)
from sdk.api_client.models.technical_asset_status import TechnicalAssetStatus
from sdk.api_client.models.technical_mapping import TechnicalMapping

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Environment configurations
agent_configs_path = os.environ.get("PROV_AGENT_CONFIGS_PATH", "/agent_configs")
demo_db_host = os.environ.get("PROV_DEMO_DB_HOST", "postgresql-demo")
demo_db_port = int(os.environ.get("PROV_DEMO_DB_PORT", "5432"))
demo_db_name = os.environ.get("PROV_DEMO_DB_NAME", "dpp_demo")
demo_db_admin_user = os.environ.get("PROV_DEMO_DB_ADMIN_USER", "postgres")
demo_db_admin_password = os.environ.get("PROV_DEMO_DB_ADMIN_PASSWORD", "abc123")

FINALIZER_NAME = "postgres-agent-provisioner"


class DataProductReconciler(Reconciler):
    def __init__(self, client: Client | AuthenticatedClient) -> None:
        self._client = client
        self._lifecycle_cache: list[DataProductLifeCyclesGetItem] = []
        self._platform_config_cache: list[PlatformServiceConfiguration] = []

    async def list_ids(self) -> Iterable[UUID]:
        """Startup resync: Fetch all existing Data Product IDs via SDK."""
        response = await get_data_products.asyncio(client=self._client)
        if isinstance(response, GetDataProductsResponse):
            return [data_product.id for data_product in response.data_products]
        if isinstance(response, HTTPValidationError):
            raise Exception(response.detail)
        return []

    async def reconcile(self, resource_id: UUID) -> None:
        """Main idempotent loop aligning infrastructure with the SDK models."""
        # 1. Fetch desired state using SDK API
        dp = await get_data_product.asyncio(id=resource_id, client=self._client)
        if dp is None or isinstance(dp, HTTPValidationError):
            logging.warning(
                f"Skipping reconciliation; data product {resource_id} not found or invalid."
            )
            return

        # 2. Handle deletion path (De-provisioning)
        if dp.status == AbstractDataProductStatus.DELETING:
            logging.info(
                f"Data product {resource_id} is deleting. Cleaning up infrastructure..."
            )
            await self._deprovision(dp.namespace)

            await remove_data_product_finalizer.asyncio(
                id=resource_id,
                finalizer=FINALIZER_NAME,
                client=self._client,
            )
            return

        # 3. Handle active/live path (Provisioning)
        if FINALIZER_NAME not in (dp.finalizers or []):
            await add_data_product_finalizer.asyncio(
                id=resource_id,
                body=FinalizerRequest(finalizer=FINALIZER_NAME),
                client=self._client,
            )

        namespace = dp.namespace
        name = dp.name
        schema_name = namespace.replace("-", "_")
        db_user = f"{schema_name}_user"
        db_password = f"{schema_name}_pwd"

        # Ensure DB Schema and User exist
        self._provision_db_schema(schema_name, db_user, db_password)

        # Ensure Platform Technical Assets exist
        await self._ensure_technical_assets(
            resource_id, dp, name, namespace, schema_name
        )

        # Resolve all approved inputs from incoming links via SDK
        input_ports_response = await get_data_product_input_ports.asyncio(
            id=resource_id, client=self._client
        )

        approved_providers = []
        if isinstance(input_ports_response, GetDataProductInputPortsResponse):
            for ip in input_ports_response.input_ports:
                if ip.status == "approved":
                    provider_dp_id = ip.output_port.data_product_id
                    if provider_dp_id:
                        provider_dp = await get_data_product.asyncio(
                            id=provider_dp_id, client=self._client
                        )
                        if isinstance(provider_dp, GetDataProductResponse):
                            approved_providers.append(provider_dp)

        # Apply DB Grants from approved incoming links
        for provider in approved_providers:
            provider_schema = provider.namespace.replace("-", "_")
            self._grant_db_access(provider_schema, db_user)

        # Rewrite the agent configuration file using the fresh source of truth
        self._write_agent_config(
            dp, approved_providers, schema_name, db_user, db_password
        )

        # Advance Lifecycle to "Ready" if it isn't already there
        await self._ensure_lifecycle_ready(resource_id, dp)

    # --- Helper methods ---

    @classmethod
    def _get_db_connection(cls):
        return psycopg2.connect(
            host=demo_db_host,
            port=demo_db_port,
            dbname=demo_db_name,
            user=demo_db_admin_user,
            password=demo_db_admin_password,
        )

    def _provision_db_schema(self, schema_name: str, db_user: str, db_password: str):
        conn = self._get_db_connection()
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
                cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
                if not cur.fetchone():
                    cur.execute(
                        f"CREATE USER {db_user} WITH PASSWORD %s", (db_password,)
                    )
                cur.execute(f"GRANT USAGE ON SCHEMA {schema_name} TO {db_user}")
                cur.execute(
                    f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema_name} TO {db_user}"
                )
        finally:
            conn.close()

    def _grant_db_access(self, provider_schema: str, consumer_user: str):
        conn = self._get_db_connection()
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"GRANT USAGE ON SCHEMA {provider_schema} TO {consumer_user}"
                )
                cur.execute(
                    f"GRANT SELECT ON ALL TABLES IN SCHEMA {provider_schema} TO {consumer_user}"
                )
        finally:
            conn.close()

    async def _ensure_technical_assets(
        self,
        resource_id: UUID,
        dp: GetDataProductResponse,
        name: str,
        namespace: str,
        schema_name: str,
    ):
        assets_response = await get_data_product_technical_assets.asyncio(
            data_product_id=resource_id, client=self._client
        )
        existing_assets = (
            assets_response.technical_assets
            if isinstance(assets_response, GetTechnicalAssetsResponse)
            else []
        )
        configs = await self._get_platform_configs()

        if not any(
            a.configuration.configuration_type
            == "OSISemanticModelTechnicalAssetConfiguration"
            for a in existing_assets
        ):
            osi_cfg = next((c for c in configs if c.service.name == "OSI"), None)
            if osi_cfg:
                configuration = OSISemanticModelTechnicalAssetConfiguration(
                    configuration_type="OSISemanticModelTechnicalAssetConfiguration",
                    model_name=f"{name} Semantic Model",
                    location=f"/products/{namespace}/osi.yml",
                )
                await self._create_technical_asset(
                    resource_id, dp, osi_cfg, configuration, f"{namespace}-semantic"
                )

        if not any(
            a.configuration.configuration_type
            == "PostgreSQLTechnicalAssetConfiguration"
            for a in existing_assets
        ):
            pg_cfg = next((c for c in configs if c.service.name == "PostgreSQL"), None)
            if pg_cfg:
                configuration = PostgreSQLTechnicalAssetConfiguration(
                    configuration_type="PostgreSQLTechnicalAssetConfiguration",
                    database=demo_db_name,
                    schema=schema_name,
                    access_granularity=AccessGranularity.SCHEMA,
                    table="*",
                )
                await self._create_technical_asset(
                    resource_id, dp, pg_cfg, configuration
                )

    async def _create_technical_asset(
        self,
        resource_id: UUID,
        dp: GetDataProductResponse,
        config: PlatformServiceConfiguration,
        payload_config: Any,
        custom_namespace: str | None = None,
    ):
        body = CreateTechnicalAssetRequest(
            name=dp.name,
            namespace=custom_namespace or dp.namespace,
            description=dp.description,
            tag_ids=[t.id for t in dp.tags],
            technical_mapping=TechnicalMapping.CUSTOM,
            platform_id=config.platform.id,
            service_id=config.service.id,
            configuration=payload_config,
        )

        asset_result = await create_technical_asset.asyncio(
            data_product_id=resource_id, body=body, client=self._client
        )
        if asset_result is None or isinstance(asset_result, HTTPValidationError):
            raise Exception(
                f"Failed to create technical asset for data product {resource_id}"
            )
        else:
            logging.info(
                f"Successfully created technical asset {asset_result.id}. Activating..."
            )

        # Activate via SDK model status updates
        await update_technical_asset_status.asyncio(
            data_product_id=resource_id,
            id=asset_result.id,
            body=DataOutputStatusUpdate(status=TechnicalAssetStatus.ACTIVE),
            client=self._client,
        )

    @classmethod
    def _write_agent_config(
        cls,
        dp: GetDataProductResponse,
        approved_providers: list[GetDataProductResponse],
        schema_name: str,
        db_user: str,
        db_password: str,
    ):
        namespace = dp.namespace
        about = dp.about or ""
        instructions = re.sub(r"<[^>]+>", " ", about).strip()
        instructions = re.sub(r"\s+", " ", instructions)

        osi_files = [f"/products/{namespace}/osi.yml"]
        allowed_schemas = [schema_name]

        for provider in approved_providers:
            prov_ns = provider.namespace
            osi_files.append(f"/products/{prov_ns}/osi.yml")
            allowed_schemas.append(prov_ns.replace("-", "_"))

        config = {
            "name": f"{dp.name} Agent",
            "description": dp.description,
            "instructions": instructions,
            "osi_files": osi_files,
            "allowed_schemas": allowed_schemas,
            "postgres": {
                "host": demo_db_host,
                "port": demo_db_port,
                "database": demo_db_name,
                "user": db_user,
                "password": db_password,
            },
        }

        os.makedirs(agent_configs_path, exist_ok=True)
        config_path = os.path.join(agent_configs_path, f"{namespace}.yml")
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

    async def _ensure_lifecycle_ready(
        self, resource_id: UUID, dp: GetDataProductResponse
    ):
        if dp.lifecycle is not None and dp.lifecycle.name == "Ready":
            return

        lifecycles = await self._get_lifecycles()
        ready_lc = next((lc for lc in lifecycles if lc.name == "Ready"), None)
        if not ready_lc:
            logging.error("Ready lifecycle state configuration missing on Portal.")
            return

        update_payload = DataProductUpdate(
            name=dp.name,
            namespace=dp.namespace,
            description=dp.description,
            type_id=dp.type_.id,
            lifecycle_id=ready_lc.id,
            domain_id=dp.domain.id,
            tag_ids=[tag.id for tag in dp.tags],
        )
        await update_data_product.asyncio(
            id=resource_id, body=update_payload, client=self._client
        )

    @classmethod
    async def _deprovision(cls, namespace: str | None):
        if not namespace:
            return
        config_path = os.path.join(agent_configs_path, f"{namespace}.yml")
        if os.path.exists(config_path):
            os.remove(config_path)
            logging.info(f"Removed agent config file: {config_path}")

    async def _get_lifecycles(self) -> list[DataProductLifeCyclesGetItem]:
        if not self._lifecycle_cache:
            resp = await get_data_products_lifecycles.asyncio(client=self._client)
            if resp is not None and not isinstance(resp, HTTPValidationError):
                self._lifecycle_cache = resp.data_product_life_cycles
        return self._lifecycle_cache

    async def _get_platform_configs(self) -> list[PlatformServiceConfiguration]:
        if not self._platform_config_cache:
            resp = await get_all_platform_service_configurations.asyncio(
                client=self._client
            )
            if resp is not None and not isinstance(resp, HTTPValidationError):
                self._platform_config_cache = resp.platform_service_configurations
        return self._platform_config_cache
