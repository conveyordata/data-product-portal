from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.data_products.schema import DataProduct
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


class RoleAssignmentResponse(ORMModel):
    id: UUID
    data_product: DataProduct
    user: User
    role: Role
    decision: DecisionStatus
    requested_on: Optional[datetime]
    requested_by: Optional[User]
    decided_on: Optional[datetime]
    decided_by: Optional[User]


class RoleAssignment(RoleAssignmentResponse):
    data_product_id: UUID
    user_id: UUID
    role_id: UUID


class UpdateRoleAssignment(ORMModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None
