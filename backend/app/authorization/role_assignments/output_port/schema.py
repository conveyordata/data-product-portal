from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from pydantic import BaseModel

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.model import (
    DatasetRoleAssignmentModel,
)
from app.authorization.roles.schema import Role
from app.data_products.output_ports.schema import Dataset, OutputPort
from app.shared.schema import ORMModel
from app.users.schema import User


@deprecated("Use RequestRoleAssignment or CreateOutputPortRoleAssignment instead")
class CreateOutputPortRoleAssignmentOld(BaseModel):
    user_id: UUID
    role_id: UUID


class CreateOutputPortRoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID
    output_port_id: UUID


class RequestOutputPortRoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID
    output_port_id: UUID


class DecideOutputPortRoleAssignment(BaseModel):
    decision: DecisionStatus


class ModifyOutputPortRoleAssignment(BaseModel):
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
        orm_model = DatasetRoleAssignmentModel


class OutputPortRoleAssignmentResponse(ORMModel):
    id: UUID
    output_port: OutputPort
    user: User
    role: Optional[Role]
    decision: DecisionStatus
    requested_on: Optional[datetime]
    requested_by: Optional[User]
    decided_on: Optional[datetime]
    decided_by: Optional[User]


class ListOutputPortRoleAssignmentsResponse(ORMModel):
    role_assignments: Sequence[OutputPortRoleAssignmentResponse]


@deprecated("Use RoleAssignment instead")
class RoleAssignmentOld(RoleAssignmentResponseOld):
    dataset_id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class OutputPortRoleAssignment(OutputPortRoleAssignmentResponse):
    output_port_id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class UpdateOutputPortRoleAssignment(BaseModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None


class DeleteOutputPortRoleAssignmentResponse(ORMModel):
    id: UUID
    output_port_id: UUID
