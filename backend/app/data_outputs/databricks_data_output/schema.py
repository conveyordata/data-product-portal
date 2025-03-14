from typing import Literal, Self

from pydantic import Field, model_validator

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.databricks_data_output.model import (
    DatabricksDataOutput as DatabricksDataOutputModel,
)
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_products.schema_base import BaseDataProduct


class DatabricksDataOutput(BaseDataOutputConfiguration):
    catalog: str = Field(..., description="Catalog linked to the data output")
    schema: str = Field(
        "", description="Schema of the catalog linked to the data output"
    )
    table: str = Field("*", description="Table used for the data output")
    configuration_type: Literal[DataOutputTypes.DatabricksDataOutput] = Field(
        ..., description="Type of the data output configuration"
    )
    bucket_identifier: str = Field(
        "", description="Bucket identifier for the data output"
    )
    catalog_path: str = Field("", description="Catalog path for the data output")
    table_path: str = Field("", description="Table path for the data output")

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
