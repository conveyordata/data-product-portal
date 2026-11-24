import re
from enum import Enum
from typing import Annotated, Optional, Type, TypeVar

from fastapi import Query
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import UUID, and_, exists, select
from sqlalchemy.orm import Mapper, Session

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.configuration.data_product_settings.model import DataProductSetting
from app.plugins.registry import plugin_registry
from app.settings import settings
from app.shared.schema import ORMModel

OM = TypeVar("OM", bound=ORMModel)


class ResourceNameValidityType(str, Enum):
    VALID = "VALID"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_CHARACTERS = "INVALID_CHARACTERS"
    DUPLICATE = "DUPLICATE"


class ResourceNameValidation(BaseModel):
    validity: ResourceNameValidityType


class ResourceNameSuggestion(BaseModel):
    resource_name: str


class ResourceNameLengthLimits(BaseModel):
    max_length: int


class ResourceNameService:
    max_length: int = settings.NAMESPACE_MAX_LENGTH

    def __init__(self, model: Type[OM] | Mapper[Type[OM]]):
        self.model = model

    @classmethod
    def _resource_name_from_name(cls, name: str, max_length: int) -> str:
        resource_name = re.sub(
            r"[^a-z0-9+=,.@_-]", "", name.lower().replace(" ", "-")
        ).strip("-")[:max_length]
        return "" if set(resource_name) <= {"."} else resource_name

    def _is_unique(
        self,
        resource_name: str,
        db: Session,
        scope: Optional[UUID | DataProductSettingScope] = None,
    ) -> bool:
        return not db.scalar(
            select(exists().where(self.model.namespace == resource_name))
        )

    @classmethod
    def resource_name_suggestion(
        cls, name: str, technical_asset_type: str | None = None
    ) -> ResourceNameSuggestion:
        max_length = (
            plugin_registry.get(technical_asset_type)
            .get_platform_metadata()
            .namespace_max_length
            if technical_asset_type is not None
            else cls.max_length
        )
        resource_name = cls._resource_name_from_name(name, max_length)

        return ResourceNameSuggestion(
            resource_name=resource_name,
        )

    def validate_resource_name(
        self,
        resource_name: str,
        db: Session,
        scope: Annotated[
            UUID | DataProductSettingScope | SkipJsonSchema[None], Query()
        ] = None,
    ) -> ResourceNameValidation:
        if not (len(resource_name) <= self.max_length):
            validity = ResourceNameValidityType.INVALID_LENGTH
        elif not re.match(r"\A(?!\.+\Z)[a-z0-9+=,.@_-]+\Z", resource_name):
            validity = ResourceNameValidityType.INVALID_CHARACTERS
        elif not self._is_unique(resource_name, db, scope):
            validity = ResourceNameValidityType.DUPLICATE
        else:
            validity = ResourceNameValidityType.VALID

        return ResourceNameValidation(validity=validity)

    @classmethod
    def resource_name_length_limits(
        cls,
    ) -> ResourceNameLengthLimits:
        return ResourceNameLengthLimits(
            max_length=cls.max_length,
        )


class DataProductSettingResourceNameValidator(ResourceNameService):
    def __init__(self):
        super().__init__(model=DataProductSetting)

    def _is_unique(
        self,
        resource_name: str,
        db: Session,
        scope: Optional[DataProductSettingScope] = None,
    ) -> bool:
        if scope is None:
            raise ValueError(
                "DataProductSettingResourceNameValidator requires "
                "a scope to determine uniqueness"
            )

        return not db.scalar(
            select(
                exists().where(
                    and_(
                        DataProductSetting.namespace == resource_name,
                        DataProductSetting.scope == scope,
                    )
                )
            )
        )
