from typing import Optional
from uuid import UUID

from app.core.authz.actions import AuthorizationAction
from app.shared.schema import ORMModel


class AccessRequest(ORMModel):
    object_id: Optional[UUID]
    domain: Optional[str]
    action: AuthorizationAction


class AccessResponse(ORMModel):
    access: bool
