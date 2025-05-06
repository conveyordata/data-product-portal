from uuid import UUID

from app.data_product_memberships.enums import DataProductUserRole
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel


class DataProductMembershipBasic(ORMModel):
    id: UUID
    status: DecisionStatus
    data_product_id: UUID
    user_id: UUID
    role: DataProductUserRole
