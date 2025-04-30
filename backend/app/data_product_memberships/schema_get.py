from datetime import datetime
from uuid import UUID

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_products.schema_basic import DataProductBasic
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
    # Nested schemas
    user: User
    data_product: DataProductBasic


class DataProductMembershipsGet(BaseDataProductMembershipGet):
    pass
