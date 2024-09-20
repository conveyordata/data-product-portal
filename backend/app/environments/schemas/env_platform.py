import json
from uuid import UUID

from pydantic import field_validator

from app.shared.schema import IdNameSchema, ORMModel


class _AWSConfig(ORMModel):
    account_id: str
    region: str
    can_read_from: list[str]


class EnvPlatformConfig(ORMModel):
    id: UUID
    config: _AWSConfig
    environment: IdNameSchema
    platform: IdNameSchema

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v
