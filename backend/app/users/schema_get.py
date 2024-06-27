from uuid import UUID

from pydantic import EmailStr

from app.data_product_memberships.enums import (
    DataProductUserRole,
    DataProductMembershipStatus,
)
from app.data_products.schema import DataProduct
from app.data_products.schema_get import DataProductGet
from app.shared.schema import ORMModel


class UserMembershipGet(ORMModel):
    id: UUID
    user_id: UUID
    data_product_id: UUID
    role: DataProductUserRole
    data_product: DataProduct
    status: DataProductMembershipStatus


class UserGet(ORMModel):
    email: EmailStr
    external_id: str
    first_name: str
    last_name: str
    data_product_memberships: list[UserMembershipGet]
    data_products: list[DataProductGet]
