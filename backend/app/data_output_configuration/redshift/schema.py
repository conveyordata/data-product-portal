from typing import ClassVar, List, Literal, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    RedshiftConfig,
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
from app.data_output_configuration.redshift.model import (
    RedshiftDataOutput as RedshiftDataOutputModel,
)
from app.data_products.schema import DataProduct


class RedshiftDataOutput(AssetProviderPlugin):
    name: ClassVar[str] = "RedshiftDataOutput"
    version: ClassVar[str] = "1.0"

    database: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.RedshiftDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    entire_schema: bool = False

    _platform_metadata = PlatformMetadata(
        display_name="Redshift",
        icon_name="aws-redshift-logo.svg",
        platform_key="redshift",
        parent_platform="aws",
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
    )

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
    def get_ui_metadata(cls, db: Session) -> List[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementSelect(
                name="database",
                label="Database",
                required=True,
                use_namespace_when_not_source_aligned=True,
                options=cls.get_platform_options(db),
            ),
            UIElementString(
                name="schema",
                label="Schema suffix",
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
