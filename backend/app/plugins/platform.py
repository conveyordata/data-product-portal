from typing import ClassVar, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.shared.schema import ORMModel
from app.technical_asset_configuration.base_schema import (
    TechnicalAssetPlugin,
    icon_data_uri,
)
from app.users.schema import User


class OverridableProperty(ORMModel):
    name: str
    label: str
    allowed_values: list[str]
    default: str


class ToolType(ORMModel):
    name: str
    display_name: str
    overridable_properties: list[OverridableProperty] = []


class NoSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Platform:
    key: ClassVar[str]
    display_name: ClassVar[str]
    icon_name: ClassVar[str]
    icon_package: ClassVar[Optional[str]] = None
    has_environments: ClassVar[bool] = True
    settings_model: ClassVar[type[BaseModel]] = NoSettings
    asset_types: ClassVar[list[type[TechnicalAssetPlugin]]] = []
    tool_types: ClassVar[list[ToolType]] = []

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        raise NotImplementedError

    @classmethod
    def get_icon_data_uri(cls) -> Optional[str]:
        return icon_data_uri(cls.icon_package, cls.icon_name)
