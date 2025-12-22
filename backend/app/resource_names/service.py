import re
from enum import Enum
from typing import Final, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import UUID, and_, exists, select
from sqlalchemy.orm import Mapper, Session

from app.configuration.data_product_settings.enums import DataProductSettingScope
from app.configuration.data_product_settings.model import DataProductSetting
from app.data_outputs.model import DataOutput
from app.settings import settings
from app.shared.schema import ORMModel

OM = TypeVar("OM", bound=ORMModel)


class ResourceNameValidityType(str, Enum):
    VALID = "VALID"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_CHARACTERS = "INVALID_CHARACTERS"
    DUPLICATE_NAMESPACE = "DUPLICATE_NAMESPACE"


class ResourceNameValidation(BaseModel):
    validity: ResourceNameValidityType


class ResourceNameSuggestion(BaseModel):
    resource_name: str


class ResourceNameLengthLimits(BaseModel):
    max_length: int


class ResourceNameService:
    max_length: Final[int] = settings.NAMESPACE_MAX_LENGTH

    def __init__(self, model: Type[OM] | Mapper[Type[OM]]):
        self.model = model

    @classmethod
    def _resource_name_from_name(cls, name: str) -> str:
        resource_name = re.sub(
            r"[^a-z0-9+=,.@_-]", "", name.lower().replace(" ", "-")
        ).strip("-")
        return resource_name[: cls.max_length]

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
    def resource_name_suggestion(cls, name: str) -> ResourceNameSuggestion:
        resource_name = cls._resource_name_from_name(name)

        return ResourceNameSuggestion(
            resource_name=resource_name,
        )

    def validate_resource_name(
        self,
        resource_name: str,
        db: Session,
        scope: Optional[UUID | Enum] = None,
    ) -> ResourceNameValidation:
        if not (len(resource_name) <= self.max_length):
            validity = ResourceNameValidityType.INVALID_LENGTH
        elif not re.match(r"^[a-z0-9+=,.@_-]+$", resource_name):
            validity = ResourceNameValidityType.INVALID_CHARACTERS
        elif not self._is_unique(resource_name, db, scope):
            validity = ResourceNameValidityType.DUPLICATE_NAMESPACE
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


class DataOutputResourceNameValidator(ResourceNameService):
    def __init__(self):
        super().__init__(model=DataOutput)

    def _is_unique(
        self,
        resource_name: str,
        db: Session,
        data_product_id: Optional[UUID] = None,
    ) -> bool:
        if data_product_id is None:
            raise ValueError(
                "DataOutputResourceNameValidator requires a data product ID "
                "to check uniqueness with the data product as scope"
            )

        return not db.scalar(
            select(
                exists().where(
                    and_(
                        DataOutput.namespace == resource_name,
                        DataOutput.owner_id == data_product_id,
                    )
                )
            )
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
