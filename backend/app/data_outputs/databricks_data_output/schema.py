from typing import Literal, Self

from pydantic import model_validator

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.databricks_data_output.model import (
    DatabricksDataOutput as DatabricksDataOutputModel,
)
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_products.schema_base import BaseDataProduct


class DatabricksDataOutput(BaseDataOutputConfiguration):
    database: str
    database_suffix: str
    table: str
    bucket_identifier: str
    database_path: str
    table_path: str
    configuration_type: Literal[DataOutputTypes.DatabricksDataOutput]

    class Meta:
        orm_model = DatabricksDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.database_path:
            self.database_path = self.database
        if not self.table_path:
            self.table_path = self.table
        return self

    def validate_configuration(self, data_product: BaseDataProduct):
        # If product aligned
        if not self.database.startswith(data_product.external_id):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
