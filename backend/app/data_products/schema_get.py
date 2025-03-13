from typing import Annotated, Optional
from uuid import UUID

from pydantic import Field, computed_field

from app.data_outputs.schema_get import DataOutputGet
from app.data_product_lifecycles.schema import DataProductLifeCycle
from app.data_product_memberships.enums import DataProductMembershipStatus
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_product_settings.schema import DataProductSettingValue
from app.data_product_types.schema import DataProductType
from app.data_products.status import DataProductStatus
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.schema import DatasetDataProductLink
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag


class DataProductGet(ORMModel):
    id: UUID = Field(..., description="Unique identifier for the data product")
    name: str = Field(..., description="Name of the data product")
    description: str = Field(..., description="Description of the data product")
    about: Optional[str] = Field(
        None, description="Additional information about the data product"
    )
    external_id: str = Field(
        ..., description="External identifier for the data product"
    )
    tags: list[Tag] = Field(
        ..., description="List of tags associated with the data product"
    )
    status: DataProductStatus = Field(
        ..., description="Current status of the data product"
    )
    lifecycle: Optional[DataProductLifeCycle] = Field(
        None, description="Lifecycle status of the data product"
    )
    dataset_links: list[DatasetDataProductLink] = Field(
        ..., description="Links to datasets associated with the data product"
    )
    memberships: list[DataProductMembershipGet] = Field(
        ..., description="List of memberships associated with the data product"
    )
    type: DataProductType = Field(..., description="Type of the data product")
    domain: Domain = Field(..., description="Domain to which the data product belongs")
    data_outputs: list[DataOutputGet] = Field(
        ..., description="List of data outputs associated with the data product"
    )
    data_product_settings: list[DataProductSettingValue] = Field(
        ..., description="Settings for the data product"
    )
    rolled_up_tags: set[Tag] = Field(
        ..., description="Set of rolled-up tags associated with the data product"
    )


class DataProductsGet(DataProductGet):
    id: UUID = Field(..., description="Unique identifier for the data product")
    about: Optional[Annotated[str, Field(exclude=True)]] = Field(
        None, description="Additional information about the data product"
    )
    dataset_links: Annotated[list[DatasetDataProductLink], Field(exclude=True)] = Field(
        ..., description="Links to datasets associated with the data product"
    )
    memberships: Annotated[list[DataProductMembershipGet], Field(exclude=True)] = Field(
        ..., description="List of memberships associated with the data product"
    )
    data_outputs: Annotated[list[DataOutputGet], Field(exclude=True)] = Field(
        ..., description="List of data outputs associated with the data product"
    )
    rolled_up_tags: Annotated[set[Tag], Field(exclude=True)] = Field(
        set(), description="Set of rolled-up tags associated with the data product"
    )

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
