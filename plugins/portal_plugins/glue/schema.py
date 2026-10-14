from typing import ClassVar, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schemas import (
    AWSGlueConfig,
)
from app.core.aws.get_url import get_aws_plugin_url
from app.technical_asset_configuration.base_schema import (
    PluginContext,
    FieldDependency,
    PlatformMetadata,
    SelectOption,
    TechnicalAssetPlugin,
    UIElementMetadata,
    UIElementRadio,
    UIElementSelect,
    UIElementString,
)
from app.technical_asset_configuration.enums import AccessGranularity, UIElementType
from portal_plugins.glue.mcp_instructions import MCP_INSTRUCTIONS
from portal_plugins.glue.model import (
    NAME,
)
from portal_plugins.glue.model import (
    GlueTechnicalAssetConfiguration as GlueTechnicalAssetConfigurationModel,
)


class GlueTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"
    mcp_instructions: ClassVar[str] = MCP_INSTRUCTIONS

    database: str
    database_suffix: str = ""
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    access_granularity: AccessGranularity

    _platform_metadata = PlatformMetadata(
        result_string_template="{database}__{database_suffix}.{table}",
        display_name="Glue",
        icon_name="glue-logo.svg",
        icon_package="portal_plugins.glue",
        platform_key="glue",
        parent_platform="aws",
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
        detailed_name="Database",
    )

    class Meta:
        orm_model = GlueTechnicalAssetConfigurationModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.database_path:
            self.database_path = self.database
        if not self.table_path:
            self.table_path = self.table
        if self.access_granularity == AccessGranularity.Schema:
            self.table = "*"
        return self

    def validate_configuration(self, context: PluginContext, db: Session):
        if not self.database.startswith(context.data_product.namespace):
            raise ValueError("Invalid database specified")

    def render_template(self, template, **context):
        return ".".join(
            [
                part.rstrip("_")
                for part in super().render_template(template, **context).split(".")
            ]
        )

    def get_configuration(
        self, configs: list[AWSGlueConfig]
    ) -> Optional[AWSGlueConfig]:
        return next(
            (config for config in configs if config.identifier == self.database), None
        )

    # Every AWS plugin shares the AWS tile on the data product page, so they all
    # use the same get_url. The portal refuses a parent tile whose children differ.
    get_url = classmethod(get_aws_plugin_url)

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="database",
                label="Database",
                type=UIElementType.Select,
                required=True,
                use_namespace_when_not_source_aligned=True,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            UIElementMetadata(
                name="database_suffix",
                type=UIElementType.String,
                label="Database suffix",
                tooltip="The name of the database to give write access to. Defaults to data product namespace",
                required=True,
            ),
            UIElementMetadata(
                name="access_granularity",
                label="Access granularity",
                type=UIElementType.Radio,
                tooltip="Give write access to the entire schema or a single table",
                required=True,
                radio=UIElementRadio(
                    initial_value=AccessGranularity.Schema,
                    options=[
                        SelectOption(
                            label="Schema level", value=AccessGranularity.Schema
                        ),
                        SelectOption(
                            label="Table level", value=AccessGranularity.Table
                        ),
                    ],
                ),
            ),
            UIElementMetadata(
                name="table",
                label="Table",
                type=UIElementType.String,
                tooltip="The name of the table to give write access to",
                required=True,
                string=UIElementString(initial_value="*"),
                depends_on=[
                    FieldDependency(
                        field_name="access_granularity", value=AccessGranularity.Table
                    )
                ],
            ),
        ]
        return base_metadata

    @classmethod
    def get_parent_platform(cls) -> Optional[str]:
        return "aws"

    @classmethod
    def register_mcp_tools(cls, mcp: object) -> None:
        from portal_plugins.glue.mcp_tools import register_tools

        register_tools(mcp)  # type: ignore[arg-type]
