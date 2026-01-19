from typing import ClassVar, Literal, Optional, Self

from pydantic import model_validator
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schemas import (
    AWSGlueConfig,
)
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    FieldDependency,
    PlatformMetadata,
    UIElementCheckbox,
    UIElementMetadata,
    UIElementString,
    UIElementType,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.glue.model import (
    GlueDataOutput as GlueDataOutputModel,
)
from app.data_products.schema import DataProduct


class GlueDataOutput(AssetProviderPlugin):
    name: ClassVar[str] = "GlueDataOutput"
    version: ClassVar[str] = "1.0"

    database: str
    database_suffix: str = ""
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    configuration_type: Literal[DataOutputTypes.GlueDataOutput]
    entire_schema: bool = False

    _platform_metadata = PlatformMetadata(
        display_name="Glue",
        icon_name="glue-logo.svg",
        platform_key="glue",
        parent_platform="aws",
        result_label="Resulting table",
        result_tooltip="The table you can access through this technical asset",
    )

    class Meta:
        orm_model = GlueDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.database_path:
            self.database_path = self.database
        if not self.table_path:
            self.table_path = self.table

        if self.entire_schema:
            self.table = "*"
        return self

    def validate_configuration(self, data_product: DataProduct):
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
        self, configs: list[AWSGlueConfig]
    ) -> Optional[AWSGlueConfig]:
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
                options=cls.get_platform_options(db),
            ),
            UIElementMetadata(
                name="database_suffix",
                type=UIElementType.String,
                label="Database suffix",
                tooltip="The name of the database to give write access to. Defaults to data product namespace",
                required=True,
            ),
            UIElementMetadata(
                name="entire_schema",
                label="Entire schema",
                type=UIElementType.Checkbox,
                tooltip="Give write access to the entire schema instead of a single table",
                required=False,
                checkbox=UIElementCheckbox(initial_value=True),
            ),
            UIElementMetadata(
                name="table",
                label="Table",
                type=UIElementType.String,
                tooltip="The name of the table to give write access to",
                required=True,
                string=UIElementString(initial_value="*"),
                depends_on=[FieldDependency(field_name="entire_schema", value=False)],
            ),
        ]
        return base_metadata

    @classmethod
    def get_parent_platform(cls) -> Optional[str]:
        return "aws"
