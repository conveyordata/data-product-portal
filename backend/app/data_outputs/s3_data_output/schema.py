from app.data_outputs.data_output_types import DataOutputTypes
from app.data_products.schema_base import BaseDataProduct
from app.shared.schema import ORMModel


class S3DataOutput(ORMModel):
    bucket: str
    suffix: str = ""
    path: str
    configuration_type: DataOutputTypes = DataOutputTypes.S3DataOutput

    def validate_configuration(self, data_product: BaseDataProduct):
        # TODO
        # if not self.suffix.startswith(data_product.external_id):
        #     raise ValueError("Invalid suffix specified")
        pass

    def on_create(self):
        # TODO Automatically create everything? To be seen
        # Will this replace terraform? Should we read the config from terraform?
        # client = get_client("s3")
        # client.put_object(Bucket=self.bucket, Key=self.prefix, Body="")
        pass
