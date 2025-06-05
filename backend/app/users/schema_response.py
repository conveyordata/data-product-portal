from typing import Sequence
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


class UserGet(BaseUserGet):
    pass


class UsersGet(BaseUserGet):
    global_roles: Sequence[RoleAssignmentResponse]
