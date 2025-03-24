from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Role
from app.shared.schema import ORMModel
from app.users.schema import User


class CreateRoleAssignment(BaseModel):
    data_product_id: UUID
    user_id: UUID
    role_id: UUID


class DecideRoleAssignment(BaseModel):
    decision: DecisionStatus


class ModifyRoleAssignment(BaseModel):
    role_id: UUID


class RoleAssignment(ORMModel):
    id: UUID
    data_product_id: UUID
    user: User
    role: Role
    decision: DecisionStatus
    requested_on: datetime
    requested_by: User
    decided_on: datetime
    decided_by: User


class UpdateRoleAssignment(ORMModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None
