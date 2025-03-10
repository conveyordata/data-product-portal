from enum import StrEnum
from typing import Optional
from uuid import UUID

from app.core.authz.actions import AuthorizationAction
from app.shared.schema import ORMModel


class Scope(StrEnum):
    DATASET = "dataset"
    DATA_PRODUCT = "data_product"
    DOMAIN = "domain"
    GLOBAL = "global"


class CreateRole(ORMModel):
    name: str
    scope: Scope
    description: str
    permissions: list[AuthorizationAction]


class Role(CreateRole):
    id: UUID


class UpdateRole(ORMModel):
    id: UUID
    name: Optional[str] = None
    scope: Optional[Scope] = None
    description: Optional[str] = None
    permissions: Optional[list[AuthorizationAction]] = None
