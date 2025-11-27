from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from pydantic import BaseModel

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import DatasetRoleAssignment
from app.authorization.roles.schema import Role
from app.datasets.schema import Dataset, OutputPort
from app.shared.schema import ORMModel
from app.users.schema import User


@deprecated("Use RequestRoleAssignment or CreateRoleAssignment instead")
class CreateRoleAssignmentOld(BaseModel):
    user_id: UUID
    role_id: UUID


class CreateRoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID
    output_port_id: UUID


class RequestRoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID
    output_port_id: UUID


class DecideRoleAssignment(BaseModel):
    decision: DecisionStatus


class ModifyRoleAssignment(BaseModel):
    role_id: UUID


@deprecated("Use RoleAssignmentResponse instead")
class RoleAssignmentResponseOld(ORMModel):
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


class RoleAssignmentResponse(ORMModel):
    id: UUID
    output_port: OutputPort
    user: User
    role: Optional[Role]
    decision: DecisionStatus
    requested_on: Optional[datetime]
    requested_by: Optional[User]
    decided_on: Optional[datetime]
    decided_by: Optional[User]


class ListRoleAssignmentsResponse(ORMModel):
    role_assignments: Sequence[RoleAssignmentResponse]


@deprecated("Use RoleAssignment instead")
class RoleAssignmentOld(RoleAssignmentResponseOld):
    dataset_id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class RoleAssignment(RoleAssignmentResponse):
    output_port_id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class UpdateRoleAssignment(BaseModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None
