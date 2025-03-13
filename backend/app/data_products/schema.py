from typing import Annotated, List
from uuid import UUID

from annotated_types import MinLen
from pydantic import BaseModel, Field, field_validator

from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_memberships.schema import (
    DataProductMembershipCreate,
)
from app.data_products.schema_base import BaseDataProduct
from app.data_products.status import DataProductStatus
from app.shared.schema import ORMModel


class DataProductCreate(BaseDataProduct):
    memberships: Annotated[list[DataProductMembershipCreate], MinLen(1)] = Field(
        ...,
        description=(
            "The list of memberships of" "the data product, shows owners and members"
        ),
    )
    domain_id: UUID = Field(..., description="The domain id of the data product")
    tag_ids: list[UUID] = Field(..., description="The list of tags of the data product")
    lifecycle_id: UUID = Field(
        ...,
        description=(
            "The lifecycleid of the data product, "
            "the lifecycle is a user defined state",
        ),
    )

    @field_validator("memberships", mode="after")
    @classmethod
    def contains_owner(
        cls, value: list[DataProductMembershipCreate]
    ) -> list[DataProductMembershipCreate]:
        if not any(
            membership.role == DataProductUserRole.OWNER for membership in value
        ):
            raise ValueError("Data product must have at least one owner")
        return value


class DataProductUpdate(DataProductCreate):
    pass


class DataProductAboutUpdate(ORMModel):
    about: str = Field(..., description="The about section of the data product")


class DataProductStatusUpdate(ORMModel):
    status: DataProductStatus = Field(
        ..., description="The creation state of the data product"
    )


class DataProduct(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the data product")
    name: str = Field(..., description="Name of the data product")
    description: str = Field(..., description="Description of the data product")
    tags: List[str] = Field(
        ..., description="List of tags associated with the data product"
    )
    owner_id: UUID = Field(
        ..., description="Unique identifier of the owner of the data product"
    )
    created_at: str = Field(
        ..., description="Timestamp when the data product was created"
    )
    updated_at: str = Field(
        ..., description="Timestamp when the data product was last updated"
    )
