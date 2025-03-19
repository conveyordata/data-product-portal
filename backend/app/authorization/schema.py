from typing import Optional
from uuid import UUID

from app.core.authz.actions import AuthorizationAction
from app.shared.schema import ORMModel


class AccessRequest(ORMModel):
    object_id: Optional[UUID] = None
    domain: Optional[UUID] = None
    action: AuthorizationAction


class AccessResponse(ORMModel):
    access: bool
