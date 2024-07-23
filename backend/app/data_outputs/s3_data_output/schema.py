from pydantic import field_validator

from app.data_outputs.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class S3DataOutput(ORMModel):
    bucket: str
    prefix: str
    account_id: str
    kms_key: str
    configuration_type: DataOutputTypes = DataOutputTypes.S3DataOutput

    @field_validator("bucket")
    @classmethod
    def valid_bucket_arn(cls, v: str) -> str:
        if not v.startswith("arn:aws:s3:::") or v == "arn:aws:s3:::":
            raise ValueError("Invalid arn specified")
        return v

    # TODO Add custom validators
