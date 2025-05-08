from uuid import UUID

from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.shared.schema import ORMModel


class BaseDataProductMembershipCreate(ORMModel):
    user_id: UUID
    role: DataProductUserRole

    class Meta:
        orm_model = DataProductMembershipModel


class DataProductMembershipCreate(BaseDataProductMembershipCreate):
    pass


class DataProductMembershipUpdate(BaseDataProductMembershipCreate):
    pass
