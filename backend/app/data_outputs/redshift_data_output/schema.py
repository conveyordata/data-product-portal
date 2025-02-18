from typing import Literal, Self

from pydantic import model_validator

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.redshift_data_output.model import (
    RedshiftDataOutput as RedshiftDataOutputModel,
)
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_products.schema_base import BaseDataProduct


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

    def validate_configuration(self, data_product: BaseDataProduct):
        # If product aligned
        if not self.database.startswith(data_product.external_id):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
