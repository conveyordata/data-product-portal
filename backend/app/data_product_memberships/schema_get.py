from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_product_memberships.enums import DataProductUserRole
from app.data_products.schema_basic import DataProductBasic
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema_basic import UserBasic


class BaseDataProductMembershipGet(ORMModel):
    id: UUID
    user_id: UUID
    data_product_id: UUID
    role: DataProductUserRole
    status: DecisionStatus
    requested_on: datetime

    # Nested schemas
    user: UserBasic
    data_product: DataProductBasic
    requested_by: Optional[UserBasic]
    denied_by: Optional[UserBasic]
    approved_by: Optional[UserBasic]


class DataProductMembershipGet(BaseDataProductMembershipGet):
    pass


class DataProductMembershipsGet(BaseDataProductMembershipGet):
    pass
