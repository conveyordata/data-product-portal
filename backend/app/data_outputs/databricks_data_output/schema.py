from typing import Literal, Self

from pydantic import model_validator

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.databricks_data_output.model import (
    DatabricksDataOutput as DatabricksDataOutputModel,
)
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_products.schema_base import BaseDataProduct


class DatabricksDataOutput(BaseDataOutputConfiguration):
    catalog: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.DatabricksDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    catalog_path: str = ""
    table_path: str = ""

    class Meta:
        orm_model = DatabricksDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.catalog_path:
            self.catalog_path = self.catalog
        if not self.table_path:
            self.table_path = self.table
        return self

    def validate_configuration(self, data_product: BaseDataProduct):
        # If product aligned
        if not self.catalog.startswith(data_product.external_id):
            raise ValueError("Invalid catalog specified")

    def on_create(self):
        pass
