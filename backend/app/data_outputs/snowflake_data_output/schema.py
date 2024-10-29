from typing import Literal

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_outputs.snowflake_data_output.model import (
    SnowflakeDataOutput as SnowflakeDataOutputModel,
)
from app.data_products.schema_base import BaseDataProduct


class SnowflakeDataOutput(BaseDataOutputConfiguration):
    schema: str
    schema_suffix: str
    configuration_type: Literal[DataOutputTypes.SnowflakeDataOutput]

    class Meta:
        orm_model = SnowflakeDataOutputModel

    def validate_configuration(self, data_product: BaseDataProduct):
        # If product aligned
        if not self.schema.startswith(data_product.external_id):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
