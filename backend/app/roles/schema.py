from typing import Optional
from uuid import UUID

from app.core.authz.actions import AuthorizationAction
from app.shared.schema import ORMModel


class CreateRole(ORMModel):
    name: str
    scope: str
    description: str
    permissions: list[AuthorizationAction]


class Role(CreateRole):
    id: UUID


class UpdateRole(ORMModel):
    id: UUID
    name: Optional[str] = None
    scope: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list[AuthorizationAction]] = None
