from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_product_memberships.enums import (
    DataProductUserRole,
)
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductMembership(ORMModel):
    user_id: UUID
    role: DataProductUserRole

    class Meta:
        orm_model = DataProductMembershipModel


class DataProductMembershipCreate(BaseDataProductMembership):
    pass


class DataProductMembershipUpdate(BaseDataProductMembership):
    pass


class DataProductMembership(BaseDataProductMembership):
    id: UUID
    data_product_id: UUID
    status: DecisionStatus
    requested_on: datetime
    requested_by: Optional[User]
    approved_by: Optional[User]
    approved_on: Optional[datetime]
    denied_by: Optional[User]
    denied_on: Optional[datetime]
