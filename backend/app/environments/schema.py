import json
from typing import Dict
from uuid import UUID

from pydantic import RootModel, field_validator

from app.shared.schema import ORMModel


class Environment(ORMModel):
    name: str
    context: str
    is_default: bool = False


class GetEnvironment(Environment):
    id: UUID


class _AWSS3Config(ORMModel):
    account_id: int
    name: str
    arn: str
    kms: str


class Config(RootModel[Dict[str, _AWSS3Config]]):
    pass


class EnvPlatformServiceConfig(ORMModel):
    config: Config

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v


class CreateConfigSchema(EnvPlatformServiceConfig):
    platform_id: UUID
    service_id: UUID
