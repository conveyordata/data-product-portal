from typing import Literal, Optional, Self, Sequence

from pydantic import model_validator

from app.configuration.environments.platform_service_configurations.schema_response import (
    RedshiftConfig,
)
from app.data_output_configuration.base_schema import (
    BaseDataOutputConfiguration,
    UIElementMetadata,
    UIElementType,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.redshift.model import (
    RedshiftDataOutput as RedshiftDataOutputModel,
)
from app.data_products.schema import DataProduct


class RedshiftDataOutput(BaseDataOutputConfiguration):
    database: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.RedshiftDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    entire_schema: bool = False

    class Meta:
        orm_model = RedshiftDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.database_path:
            self.database_path = self.database
        if not self.table_path:
            self.table_path = self.table
        return self

    def validate_configuration(self, data_product: DataProduct):
        # If product aligned
        if not self.database.startswith(data_product.namespace):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass

    def render_template(self, template, **context):
        return ".".join(
            [
                part.rstrip("_")
                for part in super().render_template(template, **context).split(".")
            ]
        )

    def get_configuration(
        self, configs: list[RedshiftConfig]
    ) -> Optional[RedshiftConfig]:
        return next(
            (config for config in configs if config.identifier == self.database), None
        )

    @classmethod
    def get_UI_metadata(cls) -> Sequence[UIElementMetadata]:
        base_metadata = super().get_UI_metadata()
        base_metadata.extend(
            [
                UIElementMetadata(
                    name="database",
                    type=UIElementType.Select,
                    label="Database",
                    required=True,
                    use_namespace_when_not_source_aligned=True,
                    select_mode="tags",
                    max_count=1,
                    normalize_array=True,
                ),
                UIElementMetadata(
                    name="schema",
                    label="Schema suffix",
                    type=UIElementType.String,
                    tooltip="The name of the schema to give write access to. Defaults to data product namespace",
                    required=False,
                ),
                UIElementMetadata(
                    name="entire_schema",
                    label="Entire schema",
                    type=UIElementType.Checkbox,
                    tooltip="Give write access to the entire schema instead of a single table",
                    required=False,
                    initial_value=True,
                    value_prop_name="checked",
                ),
                UIElementMetadata(
                    name="table",
                    label="Table",
                    type=UIElementType.String,
                    tooltip="The name of the table to give write access to",
                    required=True,
                    depends_on={"fieldName": "entire_schema", "value": False},
                ),
            ]
        )
        return base_metadata
