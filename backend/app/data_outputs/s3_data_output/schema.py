from typing import Literal

from pydantic import Field

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.s3_data_output.model import S3DataOutput as S3DataOutputModel
from app.data_outputs.schema_base import BaseDataOutputConfiguration
from app.data_products.schema_base import BaseDataProduct


class S3DataOutput(BaseDataOutputConfiguration):
    bucket: str = Field(..., description="Bucket name of the data output")
    suffix: str = Field("", description="Suffix used in the data output")
    path: str = Field(..., description="Path for the data output")
    configuration_type: Literal[DataOutputTypes.S3DataOutput] = Field(
        ..., description="Type of the data output configuration"
    )

    class Meta:
        orm_model = S3DataOutputModel

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
