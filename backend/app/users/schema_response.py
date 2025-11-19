from typing import Optional
from uuid import UUID

from pydantic import EmailStr

from app.role_assignments.global_.schema import RoleAssignmentResponse
from app.shared.schema import ORMModel


class BaseUserGet(ORMModel):
    id: UUID
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str
    has_seen_tour: bool
    can_become_admin: bool


class UserGet(BaseUserGet):
    pass


class UsersGet(BaseUserGet):
    global_role: Optional[RoleAssignmentResponse]
