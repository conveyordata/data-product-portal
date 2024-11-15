from typing import Literal

from pydantic import model_validator
from typing_extensions import Self

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.databricks_data_output.model import (
    DatabricksDataOutput as DatabricksDataOutputModel,
)
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_products.schema_base import BaseDataProduct


class DatabricksDataOutput(BaseDataOutputConfiguration):
    schema: str
    schema_suffix: str
    bucket_identifier: str
    schema_path: str
    configuration_type: Literal[DataOutputTypes.DatabricksDataOutput]

    class Meta:
        orm_model = DatabricksDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.schema_path:
            self.schema_path = self.schema
        return self

    def validate_configuration(self, data_product: BaseDataProduct):
        # If product aligned
        if not self.schema.startswith(data_product.external_id):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
