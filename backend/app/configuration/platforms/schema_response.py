from enum import Enum
from typing import Any, Optional, Sequence
from uuid import UUID

from app.plugins.platform import OverridableProperty
from app.shared.schema import ORMModel


class PlatformTypeKind(str, Enum):
    Asset = "asset"
    Tool = "tool"


class PlatformType(ORMModel):
    kind: PlatformTypeKind
    name: str
    display_name: str
    overridable_properties: list[OverridableProperty] = []


class Platform(ORMModel):
    key: str
    display_name: str
    icon_name: str
    icon_data_uri: Optional[str]
    has_environments: bool
    settings_schema: dict[str, Any]
    types: list[PlatformType]


class GetAllPlatformsResponse(ORMModel):
    platforms: Sequence[Platform]


class PlatformEnvironmentSettings(ORMModel):
    platform_key: str
    environment_id: UUID
    settings: dict[str, Any]
