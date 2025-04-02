from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.core.authz.actions import AuthorizationAction


class AccessRequest(BaseModel):
    object_id: Optional[UUID] = None
    domain: Optional[UUID] = None
    action: AuthorizationAction


class AccessResponse(BaseModel):
    access: bool
