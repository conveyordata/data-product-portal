import json
from uuid import UUID

from pydantic import Field, field_validator

from app.platform_services.schema import PlatformService
from app.platforms.schema import Platform
from app.shared.schema import ORMModel


class PlatformServiceConfiguration(ORMModel):
    id: UUID = Field(
        ..., description="Unique identifier for the platform service configuration"
    )
    platform: Platform = Field(
        ..., description="Platform associated with the service configuration"
    )
    service: PlatformService = Field(
        ..., description="Service associated with the platform configuration"
    )
    config: list[str] = Field(
        ..., description="Configuration settings for the platform service"
    )

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v
