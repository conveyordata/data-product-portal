from typing import ClassVar, Literal, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    SnowflakeConfig,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    FieldDependency,
    PlatformMetadata,
    SelectOption,
    UIElementMetadata,
    UIElementRadio,
    UIElementSelect,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.enums import AccessGranularity, UIElementType
from app.data_output_configuration.snowflake.model import (
    SnowflakeDataOutput as SnowflakeDataOutputModel,
)
from app.data_products.schema import DataProduct


class SnowflakeDataOutput(AssetProviderPlugin):
    name: ClassVar[str] = "SnowflakeDataOutput"
    version: ClassVar[str] = "1.0"

    database: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.SnowflakeDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    access_granularity: AccessGranularity

    _platform_metadata = PlatformMetadata(
        display_name="Snowflake",
        icon_name="snowflake-logo.svg",
        platform_key="snowflake",
        parent_platform=None,
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
        detailed_name="Schema",
    )

    class Meta:
        orm_model = SnowflakeDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.database_path:
            self.database_path = self.database
        if not self.table_path:
            self.table_path = self.table
        if self.access_granularity == AccessGranularity.Schema:
            self.table = "*"
        return self

    def validate_configuration(self, data_product: DataProduct):
        # If product aligned
        if not self.database.startswith(data_product.namespace):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass

    def render_template(self, template, **context) -> str:
        return super().render_template(template, **context).replace("-", "_")

    def get_configuration(
        self, configs: list[SnowflakeConfig]
    ) -> Optional[SnowflakeConfig]:
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
