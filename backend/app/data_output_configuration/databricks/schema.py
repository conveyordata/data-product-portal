from typing import ClassVar, List, Literal, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schemas import (
    DatabricksConfig,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    FieldDependency,
    PlatformMetadata,
    UIElementCheckbox,
    UIElementMetadata,
    UIElementSelect,
    UIElementString,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.databricks.model import (
    DatabricksDataOutput as DatabricksDataOutputModel,
)
from app.data_products.schema import DataProduct


class DatabricksDataOutput(AssetProviderPlugin):
    name: ClassVar[str] = "DatabricksDataOutput"
    version: ClassVar[str] = "1.0"

    catalog: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.DatabricksDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    catalog_path: str = ""
    table_path: str = ""
    entire_schema: bool = False

    _platform_metadata = PlatformMetadata(
        display_name="Databricks",
        icon_name="databricks-logo.svg",
        platform_key="databricks",
        parent_platform=None,
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
    )

    class Meta:
        orm_model = DatabricksDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.catalog_path:
            self.catalog_path = self.catalog
        if not self.table_path:
            self.table_path = self.table
        return self

    def validate_configuration(self, data_product: DataProduct):
        # If product aligned
        if not self.catalog.startswith(data_product.namespace):
            raise ValueError("Invalid catalog specified")

    def on_create(self):
        pass

    def get_configuration(
        self, configs: list[DatabricksConfig]
    ) -> Optional[DatabricksConfig]:
        return next(
            (config for config in configs if config.identifier == self.catalog), None
        )

    @classmethod
    def get_ui_metadata(cls, db: Session) -> List[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementSelect(
                name="catalog",
                label="Catalog",
                required=True,
                use_namespace_when_not_source_aligned=True,
                options=cls.get_platform_options(db),
            ),
            UIElementString(
                name="schema",
                label="Schema",
                tooltip="The name of the schema to give write access to. Defaults to data product namespace",
                required=True,
            ),
            UIElementCheckbox(
                name="entire_schema",
                label="Entire schema",
                tooltip="Give write access to the entire schema instead of a single table",
                required=False,
                initial_value=True,
            ),
            UIElementString(
                name="table",
                label="Table",
                tooltip="The name of the table to give write access to",
                required=True,
                initial_value="*",
                depends_on=FieldDependency(field_name="entire_schema", value=False),
            ),
        ]
        return base_metadata
