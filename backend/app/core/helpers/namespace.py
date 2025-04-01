import re
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.settings import settings


class NamespaceValidityType(Enum):
    VALID = "VALID"
    INVALID_LENGTH = "INVALID_LENGTH"
    INVALID_CHARACTERS = "INVALID_CHARACTERS"
    DUPLICATE_NAMESPACE = "DUPLICATE_NAMESPACE"


class NamespaceValidation(BaseModel):
    validity: NamespaceValidityType


class NamespaceSuggestion(BaseModel):
    namespace: str
    available: bool


class NamespaceLengthLimits(BaseModel):
    max_length: int


class NamespaceValidator:
    def __init__(self, model):
        self.max_length = settings.NAMESPACE_MAX_LENGTH
        self.model = model

    def _namespace_from_name(self, name: str) -> str:
        namespace = name.strip().lower().replace(" ", "-")
        return namespace[: settings.NAMESPACE_MAX_LENGTH]

    def _is_unique(
        self,
        namespace: str,
        db: Session,
    ) -> bool:
        return not db.query(exists().where(self.model.namespace == namespace)).scalar()

    def namespace_suggestion(
        self,
        name: str,
        db: Session,
    ) -> NamespaceSuggestion:
        namespace = self._namespace_from_name(name)
        availability = self._is_unique(namespace, db)

        return NamespaceSuggestion(
            namespace=namespace,
            available=availability,
        )

    def validate_namespace(
        self,
        namespace: str,
        db: Session,
    ) -> NamespaceValidation:
        if not (len(namespace) <= self.max_length):
            validity = NamespaceValidityType.INVALID_LENGTH
        elif not re.match(r"^[A-Za-z0-9+=,.@_-]+$", namespace):
            validity = NamespaceValidityType.INVALID_CHARACTERS
        elif not self._is_unique(namespace, db):
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
