from typing import ClassVar, List, Literal, Optional

from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schemas import (
    AWSS3Config,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
    UIElementMetadata,
    UIElementSelect,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.s3.model import S3DataOutput as S3DataOutputModel
from app.data_products.schema import DataProduct


class S3DataOutput(AssetProviderPlugin):
    name: ClassVar[str] = "S3DataOutput"
    version: ClassVar[str] = "1.0"

    bucket: str
    suffix: str = ""
    path: str
    configuration_type: Literal[DataOutputTypes.S3DataOutput]

    _platform_metadata = PlatformMetadata(
        display_name="S3",
        icon_name="s3-logo.svg",
        platform_key="s3",
        parent_platform="aws",
        result_label="Resulting path",
        result_tooltip="The path you can access through this technical asset",
    )

    class Meta:
        orm_model = S3DataOutputModel

    def validate_configuration(self, data_product: DataProduct):
        pass

    def on_create(self):
        pass

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
    def get_ui_metadata(cls, db: Session) -> List[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementSelect(
                name="bucket",
                label="Bucket",
                required=True,
                options=cls.get_platform_options(db),
            ),
            UIElementString(
                name="suffix",
                label="Suffix",
                required=True,
                initial_value="",
                hidden=True,
            ),
            UIElementString(
                name="path",
                label="Path",
                tooltip="The name of the path to give write access to",
                required=True,
            ),
        ]
        return base_metadata
