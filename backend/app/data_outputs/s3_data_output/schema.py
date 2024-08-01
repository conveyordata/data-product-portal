from app.core.aws.boto3_clients import get_client
from app.data_outputs.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class S3DataOutput(ORMModel):
    bucket: str = (
        "cvr-pbac-s3-datalake-dev-demo-eqpkja"  # TODO Should come from platform info
    )
    prefix: str
    account_id: str = "test"
    kms_key: str = "test"
    configuration_type: DataOutputTypes = DataOutputTypes.S3DataOutput

    # @field_validator("bucket")
    # @classmethod
    # def valid_bucket_arn(cls, v: str) -> str:
    #     if not v.startswith("arn:aws:s3:::") or v == "arn:aws:s3:::":
    #         raise ValueError("Invalid arn specified")
    #     return v

    # TODO Add custom validators

    def on_create(self):
        # TODO Automatically create everything? To be seen
        # Will this replace terraform? Should we read the config from terraform?
        client = get_client("s3")
        client.put_object(Bucket=self.bucket, Key=self.prefix, Body="")
