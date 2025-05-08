from datetime import datetime
from typing import Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.model import GlobalRoleAssignment
from app.roles.schema import Role
from app.shared.schema import ORMModel
from app.users.schema import User


class CreateRoleAssignment(BaseModel):
    user_id: UUID
    role_id: Union[UUID, Literal["admin"]]


class DecideRoleAssignment(BaseModel):
    decision: DecisionStatus


class ModifyRoleAssignment(BaseModel):
    role_id: Union[UUID, Literal["admin"]]


class RoleAssignmentRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class RoleAssignmentResponse(ORMModel):
    id: UUID
    user: User
    role: Role
    decision: DecisionStatus
    requested_on: Optional[datetime]
    requested_by: Optional[User]
    decided_on: Optional[datetime]
    decided_by: Optional[User]

    class Meta:
        orm_model = GlobalRoleAssignment


class RoleAssignment(RoleAssignmentResponse):
    user_id: UUID
    role_id: UUID
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class UpdateRoleAssignment(BaseModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None
