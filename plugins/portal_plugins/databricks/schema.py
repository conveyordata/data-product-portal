from typing import ClassVar, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from portal_plugins.settings import DatabricksCatalogSettings
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
from portal_plugins.databricks.model import (
    NAME,
)
from portal_plugins.databricks.model import (
    DatabricksTechnicalAssetConfiguration as DatabricksTechnicalAssetConfigurationModel,
)
from app.technical_asset_configuration.enums import AccessGranularity, UIElementType


class DatabricksTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    catalog: str
    schema: str = ""
    table: str = "*"
    bucket_identifier: str = ""
    catalog_path: str = ""
    table_path: str = ""
    access_granularity: AccessGranularity

    _platform_metadata = PlatformMetadata(
        result_string_template="{catalog}.{schema}.{table}",
        display_name="Databricks",
        icon_name="databricks-logo.svg",
        icon_package="portal_plugins.databricks",
        platform_key="databricks",
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
        detailed_name="Schema",
    )

    class Meta:
        orm_model = DatabricksTechnicalAssetConfigurationModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.catalog_path:
            self.catalog_path = self.catalog
        if not self.table_path:
            self.table_path = self.table
        if self.access_granularity == AccessGranularity.Schema:
            self.table = "*"
        return self

    def validate_configuration(self, context: PluginContext, db: Session):
        # If product aligned
        if not self.catalog.startswith(context.data_product.namespace):
            raise ValueError("Invalid catalog specified")

    def get_configuration(
        self, configs: list[DatabricksCatalogSettings]
    ) -> Optional[DatabricksCatalogSettings]:
        return next(
            (config for config in configs if config.identifier == self.catalog), None
        )

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="catalog",
                label="Catalog",
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
