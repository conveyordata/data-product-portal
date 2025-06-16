import json
from uuid import UUID

from pydantic import field_validator

from app.platform_services.schema import PlatformService
from app.platforms.schema import Platform
from app.shared.schema import ORMModel


class PlatformServiceConfiguration(ORMModel):
    id: UUID
    platform: Platform
    service: PlatformService
    config: list[str]

    @classmethod
    @field_validator("config", mode="before")
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v
