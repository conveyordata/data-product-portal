import json
from uuid import UUID

from pydantic import field_validator

from app.shared.schema import IdNameSchema, ORMModel


class Identifiers(ORMModel):
    identifiers: list[str]


class PlatformSchema(IdNameSchema):
    pass


class PlatformServiceSchema(IdNameSchema):
    pass


class PlatformServiceConfigBaseSchema(ORMModel):
    config: Identifiers

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            return json.loads(v)
        return v


class PlatformServiceConfigSchema(PlatformServiceConfigBaseSchema):
    id: UUID
    platform: PlatformSchema
    service: PlatformServiceSchema
