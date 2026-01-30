"""S3 Data Output Configuration Schema"""

from typing import ClassVar, Literal, Optional

from sqlalchemy.orm import Session

# These imports will come from the main portal package
try:
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
    from app.data_output_configuration.enums import UIElementType
    from app.data_products.schema import DataProduct

    # Import the model from the main backend
    from s3_plugin.model import S3DataOutput as S3DataOutputModel
except ImportError as e:
    # When developing the plugin standalone, these might not be available
    raise ImportError(
        f"Required dependencies from data-product-portal backend not found: {e}. "
        "This plugin must be installed in the same environment as the data-product-portal backend."
    )


class S3DataOutput(AssetProviderPlugin):
    """
    S3 Data Output Configuration Plugin

    This plugin provides S3 bucket output configuration for data products.
    It can be installed as an external package and will be automatically discovered
    by the Data Product Portal via entry points.
    """

    name: ClassVar[str] = "S3DataOutput"
    version: ClassVar[str] = "1.0"
    migration_file_path: ClassVar[str] = (
        "app/database/alembic/versions/2026_01_28_1243_s3_separate_table.py"
    )

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
        detailed_name="Path",
    )

    class Meta:
        orm_model = S3DataOutputModel

    def validate_configuration(self, data_product: DataProduct):
        """Validate S3 configuration against data product"""
        pass

    def on_create(self):
        """Hook called when configuration is created"""
        pass

    def render_template(self, template: str, **context) -> str:
        """
        Render S3 path template with configuration values

        Clean up double slashes and ensure proper path formatting
        """
        return "/".join(
            [
                part
                for part in super().render_template(template, **context).split("/")
                if part
            ]
        )

    def get_configuration(self, configs: list[AWSS3Config]) -> Optional[AWSS3Config]:
        """Get S3 bucket configuration for this output"""
        return next(
            (config for config in configs if config.identifier == self.bucket), None
        )

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        """
        Generate UI form metadata for S3 configuration

        Returns form fields for bucket selection and path configuration
        """
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
