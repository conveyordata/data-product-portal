from typing import ClassVar, Literal, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_output_configuration.azure_blob.model import (
    AzureBlobTechnicalAssetConfiguration as AzureBlobTechnicalAssetConfigurationModel,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
    UIElementMetadata,
    UIElementSelect,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import UIElementType
from app.data_products.schema import DataProduct
from app.users.schema import User


class AzureBlobTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "AzureBlobTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    storage_account: str
    path: str = ""
    resource_group: str
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

    def validate_configuration(self, data_product: DataProduct):
        pass

    def on_create(self):
        pass

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return "https://portal.azure.com/"

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            # TODO remove the non-user visible fields (resource_group) and see how to distinguish between them
            UIElementMetadata(
                name="storage_account",
                label="Storage Account",
                type=UIElementType.Select,
                required=True,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            UIElementMetadata(
                name="container_name",
                label="Container",
                required=True,
                type=UIElementType.Select,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            UIElementMetadata(
                name="resource_group",
                label="Resource Group",
                required=True,
                type=UIElementType.Select,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            UIElementMetadata(
                name="path",
                label="Path",
                required=True,
                type=UIElementType.String,
                tooltip="The name of the path to give write access to",
                string=UIElementString(initial_value=""),
            ),
        ]
        return base_metadata
