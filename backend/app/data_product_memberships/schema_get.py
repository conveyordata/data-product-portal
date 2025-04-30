from datetime import datetime
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


class DataProductMembershipGet(BaseDataProductMembershipGet):
    user: User
    data_product: BaseDataProductGet


class DataProductMembershipsGet(BaseDataProductMembershipGet):
    pass
