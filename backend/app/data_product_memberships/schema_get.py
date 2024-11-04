from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_products.schema import DataProduct
from app.shared.schema import ORMModel
from app.users.schema import User


class DataProductMembershipGet(ORMModel):
    id: UUID
    user_id: UUID
    data_product_id: UUID
    role: DataProductUserRole
    status: DataProductMembershipStatus
    user: User


class DataProductMembershipsGet(DataProductMembershipGet):
    user: Annotated[User, Field(exclude=True)]
    data_product: Annotated[DataProduct, Field(exclude=True)]
