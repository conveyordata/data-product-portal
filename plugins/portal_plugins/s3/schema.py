from typing import ClassVar, Optional

from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schemas import (
    AWSS3Config,
)
from app.core.aws.get_url import get_aws_plugin_url
from app.technical_asset_configuration.base_schema import (
    PlatformMetadata,
    TechnicalAssetPlugin,
    UIElementMetadata,
    UIElementSelect,
    UIElementString,
)
from app.technical_asset_configuration.enums import UIElementType
from portal_plugins.s3.model import (
    NAME,
)
from portal_plugins.s3.model import (
    S3TechnicalAssetConfiguration as S3TechnicalAssetConfigurationModel,
)


class S3TechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    bucket: str
    suffix: str = ""
    path: str

    _platform_metadata = PlatformMetadata(
        result_string_template="{bucket}/{suffix}/{path}",
        technical_info_template="{bucket_arn}/{suffix}/{path}/*",
        display_name="S3",
        icon_name="s3-logo.svg",
        icon_package="portal_plugins.s3",
        platform_key="s3",
        parent_platform="aws",
        result_label="Resulting path",
        result_tooltip="The path you can access through this technical asset",
        detailed_name="Path",
    )

    class Meta:
        orm_model = S3TechnicalAssetConfigurationModel

    # Every AWS plugin shares the AWS tile on the data product page, so they all
    # use the same get_url. The portal refuses a parent tile whose children differ.
    get_url = classmethod(get_aws_plugin_url)

    def render_template(self, template, **context):
        """
        Example template: {bucket_arn}/{suffix}/{path}/*
        The bucket_arn is extracted based on the bucket names configured in the env platform services config.
        The bucket name much match with the bucket name persisted for this technical asset configuration.
        """
        return "/".join(
            [
                part
                for part in super().render_template(template, **context).split("/")
                if part
            ]
        )

    def get_configuration(self, configs: list[AWSS3Config]) -> Optional[AWSS3Config]:
        """
        Filter the configuration based on the bucket
        """
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
                use_namespace_when_not_source_aligned=True,
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
