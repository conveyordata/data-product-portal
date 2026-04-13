from typing import ClassVar, Literal, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
    UIElementMetadata,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import UIElementType
from app.data_output_configuration.osi_sem_model.model import (
    OSISemanticModelTechnicalAssetConfiguration as OSISemanticModelTechnicalAssetConfigurationModel,
)
from app.data_products.schema import DataProduct
from app.users.schema import User


class OSISemanticModelTechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "OSISemanticModelTechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    model_name: str = ""
    file_path: str = ""
    configuration_type: Literal[
        DataOutputTypes.OSISemanticModelTechnicalAssetConfiguration
    ]

    _platform_metadata = PlatformMetadata(
        display_name="OSI",
        icon_name="osi-logo.svg",
        platform_key="osi",
        result_label="Resulting model",
        result_tooltip="The yaml file you can access through this technical asset",
        detailed_name="Model",
    )

    class Meta:
        orm_model = OSISemanticModelTechnicalAssetConfigurationModel

    def validate_configuration(self, data_product: DataProduct, db: Session):
        pass

    def on_create(self):
        pass

    def get_configuration(self, configs: list) -> None:
        return None

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return ""

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="model_name",
                label="Model Name",
                type=UIElementType.String,
                required=True,
            ),
            UIElementMetadata(
                name="file_path",
                label="File Path",
                type=UIElementType.String,
                required=True,
            ),
        ]
        return base_metadata
