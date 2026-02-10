from typing import ClassVar, Literal, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schemas import (
    AWSS3Config,
)
from app.core.aws.get_url import get_aws_url
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
    UIElementMetadata,
    UIElementSelect,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import UIElementType
from app.data_output_configuration.s3.model import (
    S3TechnicalAssetConfiguration as S3TechnicalAssetConfigurationModel,
)
from app.data_products.schema import DataProduct
from app.users.schema import User


class S3TechnicalAssetConfiguration(AssetProviderPlugin):
    name: ClassVar[str] = "S3TechnicalAssetConfiguration"
    version: ClassVar[str] = "1.0"

    bucket: str
    suffix: str = ""
    path: str
    configuration_type: Literal[DataOutputTypes.S3TechnicalAssetConfiguration]

    _platform_metadata = PlatformMetadata(
        display_name="S3",
        icon_name="s3-logo.svg",
        platform_key="s3",
        parent_platform="aws",
        result_label="Resulting path",
        result_tooltip="The path you can access through this technical asset",
        detailed_name="Path",
    )

    class Meta:
        orm_model = S3TechnicalAssetConfigurationModel

    def validate_configuration(self, data_product: DataProduct):
        pass

    def on_create(self):
        pass

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        if environment is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Environment is required to get the URL for S3 technical asset configurations",
            )
        return get_aws_url(id, db, actor, environment)

    def render_template(self, template, **context):
        return "/".join(
            [
                part
                for part in super().render_template(template, **context).split("/")
                if part
            ]
        )

    def get_configuration(self, configs: list[AWSS3Config]) -> Optional[AWSS3Config]:
        return next(
            (config for config in configs if config.identifier == self.bucket), None
        )

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="bucket",
                label="Bucket",
                type=UIElementType.Select,
                required=True,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            UIElementMetadata(
                name="suffix",
                label="Suffix",
                required=True,
                type=UIElementType.String,
                string=UIElementString(initial_value=""),
                hidden=True,
            ),
            UIElementMetadata(
                name="path",
                label="Path",
                type=UIElementType.String,
                tooltip="The name of the path to give write access to",
                required=True,
            ),
        ]
        return base_metadata
