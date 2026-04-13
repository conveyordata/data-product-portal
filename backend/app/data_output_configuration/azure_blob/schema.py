import logging
from typing import ClassVar, Literal, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.configuration.environments.platform_service_configurations.schemas import (
    AzureBlobConfig,
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
        """
        No filtering on blob configuration as there should only be 1 map per environment to translate domain -> storage account
        """
        return next((config for config in configs), None)

    def render_template(self, template, **context):
        """
        Example template: https://{storage_account}.blob.core.windows.net/{container_name}/{path}
        Render the template with the provided context, handling storage account resolution.
        Supports 2 different template formats for resolving the technical information:
        - The platform env configuration contains storage account names by domain. We fetch the storage account name for the domain and use it in the template.
        - There is only one storage account name assigned to the default key in the platform env configuration, we use it in the template.
        """
        logger.info("Start rendering template")
        if "{storage_account}" in template:
            storage_account_names = context.get("storage_account_names", {})
            if storage_account_names and self.domain in storage_account_names:
                context["storage_account"] = storage_account_names[self.domain]
                logger.info(f"storage account name is {context['storage_account']}")
            elif len(storage_account_names) == 1 and "default" in storage_account_names:
                context["storage_account"] = list(storage_account_names.values())[0]
                logger.info(f"storage account name is {context['storage_account']}")
            return super().render_template(template, **context)
        else:
            return super().render_template(template, **context)

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
