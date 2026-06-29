import logging
import os
import shutil
from typing import Any, Iterable, Optional
from uuid import UUID

from cookiecutter.main import cookiecutter
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
)
from sdk.api_client.api.data_products_technical_assets import (
    create_technical_asset,
    get_data_product_technical_assets,
    update_technical_asset_status,
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
    GetTechnicalAssetsResponse,
    HTTPValidationError,
    PlatformServiceConfiguration,
)
from sdk.api_client.models.access_granularity import AccessGranularity
from sdk.api_client.models.postgre_sql_technical_asset_configuration import (
    PostgreSQLTechnicalAssetConfiguration,
)
from sdk.api_client.models.technical_asset_status import TechnicalAssetStatus
from sdk.api_client.models.technical_mapping import TechnicalMapping

import sdk

# Calculate base directories relative to this script.
# Script is at demo/basic/provisioner/provisioner/reconciler.py
script_dir = os.path.dirname(os.path.abspath(__file__))
provisioner_dir = os.path.dirname(script_dir)  # demo/basic/provisioner
basic_demo_dir = os.path.dirname(provisioner_dir)  # demo/basic

template_path = os.environ.get(
    "PROV_TEMPLATE_PATH",
    os.path.join(provisioner_dir, "templates", "dbt"),
)
template_output_path = os.environ.get(
    "PROV_TEMPLATE_OUTPUT_PATH",
    os.path.join(basic_demo_dir, "products"),
)

FINALIZER_NAME = "demo-provisioner"


class DataProductReconciler(sdk.Reconciler):
    def __init__(self, client: Any):
        self._client = client

    async def list_ids(self) -> Iterable[UUID]:
        response = await get_data_products.asyncio(client=self._client)
        if response is None:
            return []
        if isinstance(response, GetDataProductsResponse):
            return [data_product.id for data_product in response.data_products]
        if isinstance(response, HTTPValidationError):
            raise Exception(response.detail)
        raise Exception("Unexpected response")

    async def _get_lifecycles(self) -> list[DataProductLifeCyclesGetItem]:
        logging.info("Fetching lifecycles from portal API")
        result = await get_data_products_lifecycles.asyncio(client=self._client)
        if result is None or isinstance(result, HTTPValidationError):
            raise Exception("Failed to fetch lifecycles")

        return result.data_product_life_cycles

    async def _get_platform_service_configurations(
        self,
    ) -> list[PlatformServiceConfiguration]:
        logging.info("Fetching platform service configurations from portal API")
        result = await get_all_platform_service_configurations.asyncio(
            client=self._client
        )
        if result is None or isinstance(result, HTTPValidationError):
            raise Exception("Failed to fetch platform service configurations")
        return result.platform_service_configurations

    @staticmethod
    def dbt_project_path(namespace: str) -> str:
        """Return the path to the dbt project for a given namespace."""
        return os.path.join(template_output_path, namespace.replace("-", "_"))

    async def handle_delete(self, details: GetDataProductResponse):
        """Handle deletion of a data product by removing the finalizer."""
        logging.info(f"Handling deletion for data product {details.id}")

        if FINALIZER_NAME in details.finalizers:
            if os.path.isdir(self.dbt_project_path(details.namespace)):
                shutil.rmtree(self.dbt_project_path(details.namespace))
            remove_finalizer_response = await remove_data_product_finalizer.asyncio(
                id=details.id,
                finalizer=FINALIZER_NAME,
                client=self._client,
            )
            if isinstance(remove_finalizer_response, HTTPValidationError):
                raise Exception(
                    f"Failed to remove finalizer {FINALIZER_NAME} from data product {details.id}"
                )
            logging.info(
                f"Successfully removed finalizer {FINALIZER_NAME} from data product {details.id}"
            )
        else:
            logging.info(
                f"Finalizer {FINALIZER_NAME} not present on data product {details.id}, skipping"
            )

    async def reconcile(self, resource_id: UUID):
        """Reconcile a single data product towards its desired provisioned state.

        This runs on startup and on every create/update event, so each step is
        idempotent: rendering is skipped when its output already exists, the
        lifecycle is only moved when it is not already ``Ready``, and the technical
        asset is reused when one already exists for the data product's namespace.
        """
        logging.info(f"Reconciling data product {resource_id}")

        # Fetch data product details
        data_product_details = await get_data_product.asyncio(
            id=resource_id, client=self._client
        )
        if data_product_details is None:
            # Data product is removed we skip reconciliation
            return
        if isinstance(data_product_details, HTTPValidationError):
            raise Exception(f"Failed to get data product details for id {resource_id}")

        if data_product_details.status is AbstractDataProductStatus.DELETING:
            await self.handle_delete(data_product_details)
            return

        if FINALIZER_NAME not in data_product_details.finalizers:
            data_product_add_finalizer = await add_data_product_finalizer.asyncio(
                id=resource_id,
                body=FinalizerRequest(finalizer=FINALIZER_NAME),
                client=self._client,
            )
            if isinstance(data_product_add_finalizer, HTTPValidationError):
                raise Exception(
                    f"Failed to add finalizer {FINALIZER_NAME} to data product {resource_id}"
                )

        namespace = data_product_details.namespace
        logging.info(f"Data product namespace: {namespace}")

        # Render the cookiecutter template (skip when it already exists)
        output_dir = self.dbt_project_path(namespace)
        if os.path.isdir(output_dir):
            logging.info(
                f"Template output already exists at {output_dir}, skipping render"
            )
        else:
            logging.info(
                f"Rendering template for namespace {namespace} at {output_dir}"
            )
            context = {"project_name": namespace}
            cookiecutter(
                template_path,
                no_input=True,
                extra_context=context,
                output_dir=template_output_path,
            )

        # Ensure the data product is in the "Ready" lifecycle state
        await self._ensure_ready_lifecycle(resource_id, data_product_details)

        # Ensure a PostgreSQL technical asset exists and is active
        await self._ensure_technical_asset(resource_id, data_product_details)

        logging.info(f"Successfully reconciled data product {resource_id}")

    async def _ensure_ready_lifecycle(
        self, resource_id: UUID, data_product_details: Any
    ) -> None:
        current_lifecycle = data_product_details.lifecycle
        if current_lifecycle is not None and current_lifecycle.name == "Ready":
            logging.info(
                f"Data product {resource_id} already in 'Ready' state, skipping"
            )
            return

        lifecycles = await self._get_lifecycles()
        ready_lifecycle = next((lc for lc in lifecycles if lc.name == "Ready"), None)
        if not ready_lifecycle:
            raise Exception("Configuration error: 'Ready' lifecycle not found.")

        update_body = DataProductUpdate(
            name=data_product_details.name,
            namespace=data_product_details.namespace,
            description=data_product_details.description,
            type_id=data_product_details.type_.id,
            lifecycle_id=ready_lifecycle.id,
            domain_id=data_product_details.domain.id,
            tag_ids=[tag.id for tag in data_product_details.tags],
        )

        logging.info(f"Updating data product {resource_id} to 'Ready' state")
        update_result = await update_data_product.asyncio(
            id=resource_id, body=update_body, client=self._client
        )
        if update_result is None or isinstance(update_result, HTTPValidationError):
            raise Exception(f"Failed to update data product state for id {resource_id}")
        logging.info(
            f"Successfully updated data product {resource_id} to 'Ready' state."
        )

    async def _ensure_technical_asset(
        self, resource_id: UUID, data_product_details: Any
    ) -> None:
        namespace = data_product_details.namespace
        database = "dpp_demo"
        schema_name = namespace.replace("-", "_")

        existing = await self._find_postgres_technical_asset(
            resource_id, schema=schema_name, database=database
        )
        if existing == HTTPValidationError:
            raise Exception(f"Failed to find technical asset for id {resource_id}")
        if existing is not None:
            logging.info(
                f"Technical asset {existing.id} for namespace '{namespace}' already exists"
            )
            await self._ensure_technical_asset_active(
                resource_id, existing.id, existing.status
            )
            return

        configs = await self._get_platform_service_configurations()
        postgres_config = next(
            (c for c in configs if c.service.name == "PostgreSQL"), None
        )
        if not postgres_config:
            raise Exception("Configuration error: 'PostgreSQL' service not found.")

        configuration = PostgreSQLTechnicalAssetConfiguration(
            configuration_type="PostgreSQLTechnicalAssetConfiguration",
            database=database,
            schema=schema_name,
            access_granularity=AccessGranularity.SCHEMA,
            table="*",
        )

        technical_asset_body = CreateTechnicalAssetRequest(
            name=data_product_details.name,
            namespace=namespace,
            description=data_product_details.description,
            tag_ids=[],
            technical_mapping=TechnicalMapping.CUSTOM,
            platform_id=postgres_config.platform.id,
            service_id=postgres_config.service.id,
            configuration=configuration,
        )

        logging.info(f"Creating technical asset for data product {resource_id}")
        technical_asset_result = await create_technical_asset.asyncio(
            data_product_id=resource_id,
            body=technical_asset_body,
            client=self._client,
        )
        if technical_asset_result is None or isinstance(
            technical_asset_result, HTTPValidationError
        ):
            raise Exception(f"Failed to create technical asset for id {resource_id}")

        technical_asset_id = technical_asset_result.id
        logging.info(
            f"Successfully created technical asset {technical_asset_id} "
            f"for data product {resource_id}."
        )
        await self._ensure_technical_asset_active(resource_id, technical_asset_id, None)

    async def _find_postgres_technical_asset(
        self, resource_id: UUID, *, database: str, schema: str
    ) -> Optional[Any]:
        result = await get_data_product_technical_assets.asyncio(
            data_product_id=resource_id, client=self._client
        )
        if result is None or isinstance(result, HTTPValidationError):
            raise Exception(f"Failed to list technical assets for id {resource_id}")
        if not isinstance(result, GetTechnicalAssetsResponse):
            raise Exception("Unexpected response listing technical assets")
        return next(
            (
                a
                for a in result.technical_assets
                if a.configuration.configuration_type
                == "PostgreSQLTechnicalAssetConfiguration"
                and a.configuration.database == database
                and a.configuration.schema == schema
            ),
            None,
        )

    async def _ensure_technical_asset_active(
        self,
        resource_id: UUID,
        technical_asset_id: UUID,
        current_status: Optional[TechnicalAssetStatus],
    ) -> None:
        if current_status == TechnicalAssetStatus.ACTIVE:
            logging.info(
                f"Technical asset {technical_asset_id} already active, skipping"
            )
            return

        status_response = await update_technical_asset_status.asyncio_detailed(
            data_product_id=resource_id,
            id=technical_asset_id,
            body=DataOutputStatusUpdate.from_dict(
                {"status": TechnicalAssetStatus.ACTIVE.value}
            ),
            client=self._client,
        )
        if status_response.status_code != 200:
            # Don't raise: the asset itself exists; status can be retried next pass.
            logging.error(
                f"Failed to set technical asset {technical_asset_id} status to active"
            )
        else:
            logging.info(
                f"Successfully set technical asset {technical_asset_id} status to active."
            )
