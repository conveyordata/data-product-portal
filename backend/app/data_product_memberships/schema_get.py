from datetime import datetime
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
    id: UUID = Field(
        ..., description="Unique identifier for the data product membership"
    )
    user_id: UUID = Field(..., description="Unique identifier of the user")
    data_product_id: UUID = Field(
        ..., description="Unique identifier of the data product"
    )
    role: DataProductUserRole = Field(
        ..., description="Role of the user in the data product"
    )
    status: DataProductMembershipStatus = Field(
        ..., description="Status of the data product membership"
    )
    user: User = Field(
        ..., description="User associated with the data product membership"
    )
    data_product: DataProduct = Field(
        ..., description="Data product associated with the membership"
    )
    requested_on: datetime = Field(
        ..., description="Timestamp when the membership was requested"
    )
    approved_by: User | None = Field(
        None, description="User who approved the membership, if applicable"
    )
    approved_on: datetime | None = Field(
        None, description="Timestamp when the membership was approved, if applicable"
    )
    denied_by: User | None = Field(
        None, description="User who denied the membership, if applicable"
    )
    denied_on: datetime | None = Field(
        None, description="Timestamp when the membership was denied, if applicable"
    )


class DataProductMembershipsGet(DataProductMembershipGet):
    user: Annotated[
        User,
        Field(
            exclude=True, description="User associated with the data product membership"
        ),
    ]
    data_product: Annotated[
        DataProduct,
        Field(exclude=True, description="Data product associated with the membership"),
    ]
