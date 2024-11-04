from typing import Annotated, Optional
from uuid import UUID

from pydantic import Field, computed_field

from app.business_areas.schema import BusinessArea
from app.data_outputs.schema_get import DataOutputGet
from app.data_product_memberships.enums import DataProductMembershipStatus
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_product_types.schema import DataProductType
from app.data_products.status import DataProductStatus
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class DatasetLink(DataProductDatasetAssociation):
    dataset: Dataset


class DataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    about: Optional[str]
    external_id: str
    tags: list[Tag]
    status: DataProductStatus
    dataset_links: list[DatasetLink]
    memberships: list[DataProductMembershipGet]
    type: DataProductType
    business_area: BusinessArea
    data_outputs: list[DataOutputGet]


class DataProductsGet(DataProductGet):
    id: UUID
    status: DataProductStatus
    about: Optional[Annotated[str, Field(exclude=True)]]
    dataset_links: Annotated[list[DatasetLink], Field(exclude=True)]
    memberships: Annotated[list[DataProductMembershipGet], Field(exclude=True)]
    data_outputs: Annotated[list[DataOutputGet], Field(exclude=True)]

    @computed_field
    def user_count(self) -> int:
        approved_memberships = [
            membership
            for membership in self.memberships
            if membership.status == DataProductMembershipStatus.APPROVED
        ]
        return len(approved_memberships)

    @computed_field
    def dataset_count(self) -> int:
        accepted_dataset_links = [
            link
            for link in self.dataset_links
            if link.status == DataProductDatasetLinkStatus.APPROVED
        ]
        return len(accepted_dataset_links)

    @computed_field
    def data_outputs_count(self) -> int:
        return len(self.data_outputs)
