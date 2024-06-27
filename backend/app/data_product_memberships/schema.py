from datetime import datetime
from uuid import UUID

from app.data_product_memberships.enums import (
    DataProductUserRole,
    DataProductMembershipStatus,
)
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
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
    status: DataProductMembershipStatus
    requested_on: datetime
    requested_by: User | None
    approved_by: User | None
    approved_on: datetime | None
    denied_by: User | None
    denied_on: datetime | None
