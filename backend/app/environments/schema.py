import json
from uuid import UUID

from pydantic import Field, field_validator

from app.shared.schema import ORMModel

from .enums import PlatformTypes


class Environment(ORMModel):
    name: str
    is_default: bool = False


class S3Config(ORMModel):
    bucket_arn: str
    prefix_path: str


class GlueConfig(ORMModel):
    db_schema: str = Field(alias="schema")
    table_prefixes: list[str]


class AWSSettings(ORMModel):
    account_id: str
    kms_key: str
    s3: S3Config
    glue: GlueConfig


class CreatePlatform(ORMModel):
    name: PlatformTypes
    settings: AWSSettings

    @field_validator("settings", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v


class Platform(CreatePlatform):
    id: UUID
