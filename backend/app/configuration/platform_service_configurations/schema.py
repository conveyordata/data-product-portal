import json
from typing import Sequence
from uuid import UUID

from pydantic import field_validator

from app.configuration.platforms.platform_services.schema import PlatformService
from app.configuration.platforms.schema_response import Platform
from app.shared.schema import ORMModel


class PlatformServiceConfiguration(ORMModel):
    id: UUID
    platform: Platform
    service: PlatformService
    config: list[str]

    @field_validator("config", mode="before")
    @classmethod
    def parse_settings(cls, v: str | list) -> list:
        if isinstance(v, str):
            return json.loads(v)
        return v


class GetAllPlatformServiceConfigurationsResponse(ORMModel):
    platform_service_configurations: Sequence[PlatformServiceConfiguration]
