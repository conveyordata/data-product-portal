import json
from uuid import UUID

from pydantic import field_validator

from app.shared.schema import ORMModel


class Environment(ORMModel):
    name: str
    context: str
    is_default: bool = False


class GetEnvironment(Environment):
    id: UUID


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
    config: list[_AWSS3Config | _AWSGlueConfig]

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class _AWSConfig(ORMModel):
    account_id: str
    region: str
    can_read_from: list[str]


class EnvPlatformConfig(ORMModel):
    config: _AWSConfig

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v
