import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from sqlalchemy import UUID, and_, exists, select
from sqlalchemy.orm import Session

from app.data_outputs.model import DataOutput
from app.data_product_settings.enums import DataProductSettingScope
from app.data_product_settings.model import DataProductSetting
from app.settings import settings


class NamespaceValidityType(str, Enum):
    VALID = "VALID"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_CHARACTERS = "INVALID_CHARACTERS"
    DUPLICATE_NAMESPACE = "DUPLICATE_NAMESPACE"


class NamespaceValidation(BaseModel):
    validity: NamespaceValidityType


class NamespaceSuggestion(BaseModel):
    namespace: str


class NamespaceLengthLimits(BaseModel):
    max_length: int


class NamespaceValidator:
    def __init__(self, model):
        self.max_length = settings.NAMESPACE_MAX_LENGTH
        self.model = model

    def _namespace_from_name(self, name: str) -> str:
        namespace = re.sub(
            r"[^a-z0-9+=,.@_-]", "", name.lower().replace(" ", "-")
        ).strip("-")
        return namespace[: settings.NAMESPACE_MAX_LENGTH]

    def _is_unique(
        self,
        namespace: str,
        db: Session,
        scope: Optional[UUID | DataProductSettingScope] = None,
    ) -> bool:
        return not db.scalar(select(exists().where(self.model.namespace == namespace)))

    def namespace_suggestion(
        self,
        name: str,
    ) -> NamespaceSuggestion:
        namespace = self._namespace_from_name(name)

        return NamespaceSuggestion(
            namespace=namespace,
        )

    def validate_namespace(
        self,
        namespace: str,
        db: Session,
        scope: Optional[UUID | Enum] = None,
    ) -> NamespaceValidation:
        if not (len(namespace) <= self.max_length):
            validity = NamespaceValidityType.INVALID_LENGTH
        elif not re.match(r"^[a-z0-9+=,.@_-]+$", namespace):
            validity = NamespaceValidityType.INVALID_CHARACTERS
        elif not self._is_unique(namespace, db, scope):
            validity = NamespaceValidityType.DUPLICATE_NAMESPACE
        else:
            validity = NamespaceValidityType.VALID

        return NamespaceValidation(validity=validity)

    def namespace_length_limits(
        self,
    ) -> NamespaceLengthLimits:
        return NamespaceLengthLimits(
            max_length=self.max_length,
        )


class DataOutputNamespaceValidator(NamespaceValidator):
    def __init__(self):
        super().__init__(model=DataOutput)

    def _is_unique(
        self,
        namespace: str,
        db: Session,
        data_product_id: Optional[UUID] = None,
    ) -> bool:
        if data_product_id is None:
            raise ValueError(
                "DataOutputNamespaceValidator requires a data product ID "
                "to check uniqueness with the data product as scope"
            )

        return not db.scalar(
            select(
                exists().where(
                    and_(
                        DataOutput.namespace == namespace,
                        DataOutput.owner_id == data_product_id,
                    )
                )
            )
        )


class DataProductSettingNamespaceValidator(NamespaceValidator):
    def __init__(self):
        super().__init__(model=DataProductSetting)

    def _is_unique(
        self,
        namespace: str,
        db: Session,
        scope: Optional[DataProductSettingScope] = None,
    ) -> bool:
        if scope is None:
            raise ValueError(
                "DataProductSettingNamespaceValidator requires "
                "a scope to determine uniqueness"
            )

        return not db.scalar(
            select(
                exists().where(
                    and_(
                        DataProductSetting.namespace == namespace,
                        DataProductSetting.scope == scope,
                    )
                )
            )
        )
