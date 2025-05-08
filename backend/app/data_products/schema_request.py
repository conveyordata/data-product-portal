from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen
from pydantic import field_validator

from app.data_product_memberships.enums import DataProductUserRole
from app.data_product_memberships.schema_request import DataProductMembershipCreate
from app.data_products.status import DataProductStatus
from app.shared.schema import ORMModel


class DataProductCreate(ORMModel):
    name: str
    namespace: str
    description: str
    type_id: UUID
    about: Optional[str] = None
    memberships: Annotated[list[DataProductMembershipCreate], MinLen(1)]
    domain_id: UUID
    tag_ids: list[UUID]
    lifecycle_id: UUID

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
