from datetime import datetime
from typing import Optional
from uuid import UUID

from app.data_product_memberships.enums import DataProductUserRole
from app.data_products.schema import DataProduct
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductMembershipGet(ORMModel):
    id: UUID
    user_id: UUID
    data_product_id: UUID
    role: DataProductUserRole
    status: DecisionStatus
    requested_on: datetime

    # Nested schemas
    user: User
    data_product: DataProduct
    requested_by: Optional[User]
    denied_by: Optional[User]
    approved_by: Optional[User]


class DataProductMembershipGet(BaseDataProductMembershipGet):
    pass


class DataProductMembershipsGet(BaseDataProductMembershipGet):
    pass
