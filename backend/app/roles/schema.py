from enum import IntEnum, StrEnum
from typing import Optional
from uuid import UUID

from app.core.authz.actions import AuthorizationAction
from app.shared.schema import ORMModel


class Scope(StrEnum):
    DATASET = "dataset"
    DATA_PRODUCT = "data_product"
    DOMAIN = "domain"
    GLOBAL = "global"


class Prototype(IntEnum):
    CUSTOM = 0
    EVERYONE = 1
    OWNER = 2
    ADMIN = 3


class CreateRole(ORMModel):
    name: str
    scope: Scope
    description: str
    permissions: list[AuthorizationAction]


class UpdateRole(ORMModel):
    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list[AuthorizationAction]] = None


class Role(CreateRole):
    id: UUID
    prototype: Prototype
