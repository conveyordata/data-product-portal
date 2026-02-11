from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID
from warnings import deprecated

from pydantic import BaseModel

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment as DataProductRoleAssignmentModel,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Role
from app.data_products.schema import DataProduct
from app.shared.schema import ORMModel
from app.users.schema import User


@deprecated("Use RequestRoleAssignment or CreateDataProductRoleAssignment instead")
class CreateDataProductRoleAssignmentOld(BaseModel):
    user_id: UUID
    role_id: UUID


class CreateDataProductRoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID
    data_product_id: UUID


class RequestDataProductRoleAssignment(BaseModel):
    user_id: UUID
    role_id: UUID
    data_product_id: UUID


class DecideDataProductRoleAssignment(BaseModel):
    decision: DecisionStatus


class ModifyDataProductRoleAssignment(BaseModel):
    role_id: UUID


class DataProductRoleAssignmentResponse(ORMModel):
    id: UUID
    data_product: DataProduct
    user: User
    role: Optional[Role]
    decision: DecisionStatus
    requested_on: Optional[datetime]
    requested_by: Optional[User]
    decided_on: Optional[datetime]
    decided_by: Optional[User]

    class Meta:
        orm_model = DataProductRoleAssignmentModel


class ListDataProductRoleAssignmentsResponse(ORMModel):
    role_assignments: Sequence[DataProductRoleAssignmentResponse]


class DataProductRoleAssignment(DataProductRoleAssignmentResponse):
    data_product_id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    requested_by_id: Optional[UUID]
    decided_by_id: Optional[UUID]


class UpdateDataProductRoleAssignment(BaseModel):
    id: UUID
    role_id: Optional[UUID] = None
    decision: Optional[DecisionStatus] = None


class DeleteDataProductRoleAssignmentResponse(ORMModel):
    id: UUID
    data_product_id: UUID
