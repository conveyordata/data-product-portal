import json
from uuid import UUID

from pydantic import field_validator

from app.shared.schema import IdNameSchema, ORMModel


class _AWSS3Config(ORMModel):
    identifier: str
    bucket_name: str
    arn: str
    kms_key: str
    is_default: bool


class _AWSGlueConfig(ORMModel):
    identifier: str
    database_name: str
    bucket_name: str
    s3_path: str


class EnvPlatformServiceConfig(ORMModel):
    id: UUID
    config: list[_AWSS3Config | _AWSGlueConfig]
    environment: IdNameSchema
    platform: IdNameSchema
    service: IdNameSchema

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v
