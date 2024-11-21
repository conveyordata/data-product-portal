from typing import Literal, Self

from pydantic import model_validator

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_outputs.snowflake_data_output.model import (
    SnowflakeDataOutput as SnowflakeDataOutputModel,
)
from app.data_products.schema_base import BaseDataProduct


class SnowflakeDataOutput(BaseDataOutputConfiguration):
    schema: str
    schema_suffix: str = ""
    configuration_type: Literal[DataOutputTypes.SnowflakeDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    schema_path: str = ""
    table_path: str = ""

    class Meta:
        orm_model = SnowflakeDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.schema_path:
            self.schema_path = self.schema
        if not self.table_path:
            self.table_path = self.table
        return self

    def validate_configuration(self, data_product: BaseDataProduct):
        # TODO Force defaul t bucket identifier if bucket = ''
        if not self.schema.startswith(data_product.external_id):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
