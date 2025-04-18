from datetime import datetime
from typing import Annotated, Optional
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
    data_product: DataProduct
    requested_on: datetime
    approved_by: Optional[User]
    approved_on: Optional[datetime]
    denied_by: Optional[User]
    denied_on: Optional[datetime]


class DataProductMembershipsGet(DataProductMembershipGet):
    user: Annotated[User, Field(exclude=True)]
    data_product: Annotated[DataProduct, Field(exclude=True)]
