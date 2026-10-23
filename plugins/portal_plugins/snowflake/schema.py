from typing import ClassVar, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from portal_plugins.settings import SnowflakeDatabaseSettings
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
from portal_plugins.snowflake.model import (
    NAME,
)
from portal_plugins.snowflake.model import (
    SnowflakeTechnicalAssetConfiguration as SnowflakeTechnicalAssetConfigurationModel,
)


class SnowflakeTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    database: str
    schema: str = ""
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    access_granularity: AccessGranularity

    _platform_metadata = PlatformMetadata(
        result_string_template="{database}.{schema}.{table}",
        display_name="Snowflake",
        icon_name="snowflake-logo.svg",
        icon_package="portal_plugins.snowflake",
        platform_key="snowflake",
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
        detailed_name="Schema",
    )

    class Meta:
        orm_model = SnowflakeTechnicalAssetConfigurationModel

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
        # If product aligned
        if not self.database.startswith(context.data_product.namespace):
            raise ValueError("Invalid database specified")

    def render_template(self, template, **context) -> str:
        return super().render_template(template, **context).replace("-", "_")

    def get_configuration(
        self, configs: list[SnowflakeDatabaseSettings]
    ) -> Optional[SnowflakeDatabaseSettings]:
        return next(
            (config for config in configs if config.identifier == self.database), None
        )

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
                name="schema",
                type=UIElementType.String,
                label="Schema",
                tooltip="The name of the schema to give write access to. Defaults to data product namespace",
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
