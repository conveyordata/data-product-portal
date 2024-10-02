from app.data_outputs.data_output_types import DataOutputTypes
from app.data_products.schema_base import BaseDataProduct
from app.shared.schema import ORMModel


class GlueDataOutput(ORMModel):
    database: str
    database_suffix: str = ""
    table: str = "*"
    bucket_identifier: str = ""
    database_path: str = ""
    table_path: str = ""
    configuration_type: DataOutputTypes = DataOutputTypes.GlueDataOutput

    def validate_configuration(self, data_product: BaseDataProduct):
        # If product aligned TODO Checks
        if not self.database_path:
            self.database_path = self.database
        if not self.table_path:
            self.table_path = self.table
        # TODO Force defaul t bucket identifier if bucket = ''
        if not self.database.startswith(data_product.external_id):
            raise ValueError("Invalid database specified")

    def on_create(self):
        pass
