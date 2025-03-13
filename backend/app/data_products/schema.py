from typing import Annotated
from uuid import UUID

from annotated_types import MinLen
from pydantic import Field, field_validator

from app.data_outputs.schema_get import DataOutputGet
from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_memberships.schema import (
    DataProductMembership,
    DataProductMembershipCreate,
)
from app.data_products.schema_base import BaseDataProduct
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class DataProductCreate(BaseDataProduct):
    memberships: Annotated[list[DataProductMembershipCreate], MinLen(1)] = Field(
        ...,
        description=(
            "List of memberships associated"
            "with the data product, must include at least one owner"
        ),
    )
    domain_id: UUID = Field(
        ...,
        description="Unique identifier of the domain to which the data product belongs",
    )
    tag_ids: list[UUID] = Field(
        ..., description="List of tag identifiers associated with the data product"
    )
    lifecycle_id: UUID = Field(
        ...,
        description=(
            "Unique identifier of the lifecycle" "associated with the data product"
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
    about: str


class DataProductStatusUpdate(ORMModel):
    status: DataProductStatus


class DataProduct(BaseDataProduct):
    id: UUID
    status: DataProductStatus
    dataset_links: list[DataProductDatasetAssociation]
    tags: list[Tag]
    memberships: list[DataProductMembership]
    domain: Domain
    data_outputs: list[DataOutputGet]
