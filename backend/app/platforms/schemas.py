import json
from uuid import UUID

from pydantic import field_validator

from app.shared.schema import ORMModel


class PlatformServiceConfigSchema(ORMModel):
    identifiers: list[str]

    @field_validator("identifiers", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class GetPlatformsSchema(ORMModel):
    id: UUID
    name: str


class GetPlatformServicesSchema(GetPlatformsSchema):
    pass
