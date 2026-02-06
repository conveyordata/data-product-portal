from datetime import datetime
from typing import Literal, Optional, Sequence, Union
from uuid import UUID

from pydantic import BaseModel

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.model import (
    GlobalRoleAssignment as GlobalRoleAssignmentModel,
)
from app.authorization.roles.schema import Role
from app.shared.schema import ORMModel
from app.users.schema import User


class CreateGlobalRoleAssignment(BaseModel):
    user_id: UUID
    role_id: Union[UUID, Literal["admin"]]


class BecomeAdmin(BaseModel):
    expiry: str


class DecideGlobalRoleAssignment(BaseModel):
    decision: DecisionStatus


class ModifyGlobalRoleAssignment(BaseModel):
    role_id: Union[UUID, Literal["admin"]]


class RoleAssignmentRequest(BaseModel):
    user_id: UUID
    role_id: UUID


class GlobalRoleAssignmentResponse(ORMModel):
    id: UUID
    user: User
    role: Role
    decision: DecisionStatus
    requested_on: Optional[datetime]
    requested_by: Optional[User]
    decided_on: Optional[datetime]
    decided_by: Optional[User]

    class Meta:
        orm_model = GlobalRoleAssignmentModel


class ListGlobalRoleAssignmentsResponse(ORMModel):
    role_assignments: Sequence[GlobalRoleAssignmentResponse]


class GlobalRoleAssignment(GlobalRoleAssignmentResponse):
    user_id: UUID
    role_id: UUID
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class UpdateGlobalRoleAssignment(BaseModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None


class DeleteGlobalRoleAssignmentResponse(ORMModel):
    id: UUID
