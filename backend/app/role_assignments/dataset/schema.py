from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.datasets.schema import Dataset
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Role
from app.shared.schema import ORMModel
from app.users.schema import User


class CreateRoleAssignment(BaseModel):
    user_id: UUID
    role_id: Optional[UUID] = None


class DecideRoleAssignment(BaseModel):
    decision: DecisionStatus


class ModifyRoleAssignment(BaseModel):
    role_id: UUID


class RoleAssignmentResponse(ORMModel):
    id: UUID
    dataset: Dataset
    user: User
    role: Optional[Role]
    decision: DecisionStatus
    requested_on: Optional[datetime]
    requested_by: Optional[User]
    decided_on: Optional[datetime]
    decided_by: Optional[User]

    class Meta:
        orm_model = DatasetRoleAssignment


class RoleAssignment(RoleAssignmentResponse):
    dataset_id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class UpdateRoleAssignment(BaseModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None
