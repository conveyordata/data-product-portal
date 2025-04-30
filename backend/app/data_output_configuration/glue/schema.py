from typing import Literal, Self

from pydantic import model_validator

from app.data_output_configuration.base_schema import BaseDataOutputConfiguration
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.data_output_configuration.glue.model import (
    GlueDataOutput as GlueDataOutputModel,
)
from app.data_products.schema_basic import DataProductBasic


class GlueDataOutput(BaseDataOutputConfiguration):
    database: str
    database_suffix: str = ""
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    configuration_type: Literal[DataOutputTypes.GlueDataOutput]

    class Meta:
        orm_model = GlueDataOutputModel

    @model_validator(mode="after")
    def validate_paths(self) -> Self:
        if not self.database_path:
            self.database_path = self.database
        if not self.table_path:
            self.table_path = self.table
        return self

    def validate_configuration(self, data_product: DataProductBasic):
        # TODO Force defaul t bucket identifier if bucket = ''
        if not self.database.startswith(data_product.namespace):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
