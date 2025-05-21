from typing import Literal, Optional, Self

from pydantic import model_validator

from app.data_output_configuration.base_schema import BaseDataOutputConfiguration
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.redshift.model import (
    RedshiftDataOutput as RedshiftDataOutputModel,
)
from app.data_products.schema import DataProduct
from app.environment_platform_service_configurations.schemas.redshift_schema import (
    RedshiftConfig,
)


class RedshiftDataOutput(BaseDataOutputConfiguration):
    database: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.RedshiftDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""

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
