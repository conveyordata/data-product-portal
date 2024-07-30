import json
from uuid import UUID

from pydantic import field_validator

from app.shared.schema import ORMModel


class Identifiers(ORMModel):
    identifiers: list[str]


class PlatformServiceConfigSchema(ORMModel):
    config: Identifiers

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v


class GetPlatformsSchema(ORMModel):
    id: UUID
    name: str


class GetPlatformServicesSchema(GetPlatformsSchema):
    pass
