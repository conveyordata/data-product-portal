from typing import Literal, Self

from pydantic import model_validator

from app.data_output_configuration.base_schema import BaseDataOutputConfiguration
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.snowflake.model import (
    SnowflakeDataOutput as SnowflakeDataOutputModel,
)
from app.data_products.schema import DataProduct


class SnowflakeDataOutput(BaseDataOutputConfiguration):
    database: str
    schema: str = ""
    configuration_type: Literal[DataOutputTypes.SnowflakeDataOutput]
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""

    class Meta:
        orm_model = SnowflakeDataOutputModel

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
