from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_products.schema_base_get import BaseDataProductGet
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductMembershipGet(ORMModel):
    id: UUID
    user_id: UUID
    data_product_id: UUID
    role: DataProductUserRole
    status: DataProductMembershipStatus
    requested_on: datetime
    approved_by: Optional[User]
    approved_on: Optional[datetime]
    denied_by: Optional[User]
    denied_on: Optional[datetime]


class DataProductMembershipGet(BaseDataProductMembershipGet):
    user: User
    data_product: BaseDataProductGet


class DataProductMembershipsGet(BaseDataProductMembershipGet):
    pass
