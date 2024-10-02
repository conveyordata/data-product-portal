from app.data_outputs.data_output_types import DataOutputTypes
from app.data_products.schema_base import BaseDataProduct
from app.shared.schema import ORMModel


class DatabricksDataOutput(ORMModel):
    database: str
    database_suffix: str
    table: str
    bucket_identifier: str
    database_path: str
    table_path: str
    configuration_type: DataOutputTypes = DataOutputTypes.DatabricksDataOutput

    def validate_configuration(self, data_product: BaseDataProduct):
        # If product aligned
        if not self.database.startswith(data_product.external_id):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
