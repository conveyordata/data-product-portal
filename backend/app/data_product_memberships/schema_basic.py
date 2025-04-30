from uuid import UUID

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.shared.schema import ORMModel


class DataProductMembershipBasic(ORMModel):
    id: UUID
    status: DataProductMembershipStatus
    data_product_id: UUID
    user_id: UUID
    role: DataProductUserRole
