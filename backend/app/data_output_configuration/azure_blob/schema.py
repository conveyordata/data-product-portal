import json
import logging
from typing import TYPE_CHECKING, ClassVar, Literal, Optional, Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.configuration.environments.platform_service_configurations.model import (
    EnvironmentPlatformServiceConfiguration,
)
from app.configuration.environments.platform_service_configurations.schemas import (
    AzureBlobConfig,
)
from app.configuration.platforms.platform_services.model import (
    PlatformService as PlatformServiceModel,
)
from app.data_output_configuration.azure_blob.model import (
    AzureBlobTechnicalAssetConfiguration as AzureBlobTechnicalAssetConfigurationModel,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
    UIElementMetadata,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import UIElementType
from app.data_products.model import DataProduct as DataProductModel
from app.data_products.schema import DataProduct
from app.users.schema import User

if TYPE_CHECKING:
    from app.configuration.environments.platform_service_configurations.schema_response import (
        EnvironmentConfigsGetItem,
    )

logger = logging.getLogger(__name__)


class AzureBlobTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "AzureBlobTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    domain: str = ""
    path: str = ""
    container_name: str

    configuration_type: Literal[DataOutputTypes.AzureBlobTechnicalAssetConfiguration]

    _platform_metadata = PlatformMetadata(
        display_name="Blob",
        icon_name="azure-storage-account-logo.svg",
        platform_key="azureblob",
        parent_platform="azure",
        result_label="Resulting path",
        result_tooltip="The path you can access through this technical asset",
        detailed_name="Path",
    )

    class Meta:
        orm_model = AzureBlobTechnicalAssetConfigurationModel

    def validate_configuration(self, data_product: DataProduct, db: Session):
        result: DataProductModel = db.scalar(
            select(DataProductModel)
            .options(selectinload(DataProductModel.domain))
            .where(DataProductModel.id == data_product.id)
        )
        logger.info(
            f"queried data product in validate configuraiton with domain: {result.domain.name}"
        )
        self.domain = result.domain.name

    def on_create(self):
        pass

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return "https://portal.azure.com/"

    def get_configuration(
        self, configs: list[AzureBlobConfig]
    ) -> Optional[AzureBlobConfig]:
        return next((config for config in configs), None)

    def render_template(self, template, **context):
        logger.info("Start rendering template")
        if "{storage_account}" in template:
            storage_account_names = context.get("storage_account_names", {})
            if storage_account_names and self.domain in storage_account_names:
                context["storage_account"] = storage_account_names[self.domain]
                logger.info(f"storage account name is {context['storage_account']}")
            elif len(storage_account_names) == 1:
                context["storage_account"] = list(storage_account_names.values())[0]
                logger.info(f"storage account name is {context['storage_account']}")
            return super().render_template(template, **context)
        else:
            return super().render_template(template, **context)

    @classmethod
    def get_domain_storage_account_mapping(cls, db: Session) -> dict[str, str]:
        """Resolve the full domain -> storage_account mapping from platform config."""
        if not cls._platform_metadata:
            raise NotImplementedError("Platform metadata not defined for this plugin")
        service = db.scalar(
            select(PlatformServiceModel).where(
                func.lower(PlatformServiceModel.name)
                == cls._platform_metadata.platform_key
            )
        )
        if not service:
            raise NotImplementedError("No platform service found")
        configs: Sequence[EnvironmentConfigsGetItem] = db.scalars(
            select(EnvironmentPlatformServiceConfiguration).where(
                EnvironmentPlatformServiceConfiguration.service_id == service.id
            )
        ).all()
        mapping: dict[str, str] = {}
        for env_config in configs:
            if not isinstance(env_config.config, str):
                continue
            service_configs = json.loads(env_config.config)
            for config_item in service_configs:
                value = config_item.get("storage_account_names")
                if isinstance(value, dict):
                    mapping.update(value)
        return mapping

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="domain",
                label="domain",
                type=UIElementType.String,
                required=False,
                hidden=True,
                string=UIElementString(initial_value=""),
            ),
            UIElementMetadata(
                name="container_name",
                label="Container",
                required=True,
                type=UIElementType.String,
                string=UIElementString(initial_value=""),
            ),
            UIElementMetadata(
                name="path",
                label="Path",
                required=False,
                type=UIElementType.String,
                tooltip="The name of the path to give write access to",
                string=UIElementString(initial_value=""),
            ),
        ]
        return base_metadata
