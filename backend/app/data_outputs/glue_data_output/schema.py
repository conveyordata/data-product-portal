from typing import Literal, Self

from pydantic import Field, model_validator

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.glue_data_output.model import (
    GlueDataOutput as GlueDataOutputModel,
)
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_products.schema_base import BaseDataProduct


class GlueDataOutput(BaseDataOutputConfiguration):
    database: str = Field(..., description="Database linked to the data output")
    database_suffix: str = Field(
        "", description="Suffix of the Database linked to the data output"
    )
    table: str = Field("*", description="Table used for the data output")
    configuration_type: Literal[DataOutputTypes.GlueDataOutput] = Field(
        ..., description="Type of the data output configuration"
    )
    bucket_identifier: str = Field(
        "", description="Bucket identifier for the data output"
    )
    database_path: str = Field("", description="Database path for the data output")
    table_path: str = Field("", description="Table path for the data output")

    class Meta:
        orm_model = GlueDataOutputModel

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
