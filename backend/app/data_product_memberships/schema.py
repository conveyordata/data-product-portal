from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.shared.schema import ORMModel
from app.users.schema import User


class BaseDataProductMembership(ORMModel):
    user_id: UUID = Field(..., description="Unique identifier of the user")
    role: DataProductUserRole = Field(
        ..., description="Role of the user in the data product"
    )

    class Meta:
        orm_model = DataProductMembershipModel


class DataProductMembershipCreate(BaseDataProductMembership):
    pass


class DataProductMembershipUpdate(BaseDataProductMembership):
    pass


class DataProductMembership(BaseDataProductMembership):
    id: UUID = Field(
        ..., description="Unique identifier for the data product membership"
    )
    data_product_id: UUID = Field(
        ..., description="Unique identifier of the data product"
    )
    status: DataProductMembershipStatus = Field(
        ..., description="Status of the data product membership"
    )
    requested_on: datetime = Field(
        ..., description="Timestamp when the membership was requested"
    )
    requested_by: User | None = Field(
        None, description="User who requested the membership, if applicable"
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
