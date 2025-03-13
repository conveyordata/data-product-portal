from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen
from pydantic import Field, computed_field

from app.data_outputs.schema_get import DataOutputGet
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_lifecycles.schema import DataProductLifeCycle
from app.data_product_settings.schema import DataProductSettingValue
from app.data_products.schema_get import DataProductsGet
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.domains.schema import Domain
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class DataProductLink(DataProductDatasetAssociation):
    data_product: DataProductsGet = Field(
        ..., description="Data product associated with the dataset link"
    )


class DataOutputLink(DataOutputDatasetAssociation):
    data_output: DataOutputGet = Field(
        ..., description="Data output associated with the dataset link"
    )


class DatasetGet(ORMModel):
    id: UUID = Field(..., description="Unique identifier for the dataset")
    external_id: str = Field(..., description="External identifier for the dataset")
    name: str = Field(..., description="Name of the dataset")
    description: str = Field(..., description="Description of the dataset")
    owners: Annotated[list[User], MinLen(1)] = Field(
        ..., description="List of users who own the dataset"
    )
    data_product_links: list[DataProductLink] = Field(
        ..., description="Links to data products associated with the dataset"
    )
    lifecycle: Optional[DataProductLifeCycle] = Field(
        None, description="Lifecycle status of the dataset"
    )
    status: DatasetStatus = Field(..., description="Current status of the dataset")
    about: Optional[str] = Field(
        None, description="Additional information about the dataset"
    )
    tags: list[Tag] = Field(..., description="List of tags associated with the dataset")
    domain: Domain = Field(..., description="Domain to which the dataset belongs")
    access_type: DatasetAccessType = Field(
        ..., description="Access type of the dataset"
    )
    data_output_links: list[DataOutputLink] = Field(
        ..., description="Links to data outputs associated with the dataset"
    )
    data_product_settings: list[DataProductSettingValue] = Field(
        ..., description="Settings for the data product"
    )
    rolled_up_tags: set[Tag] = Field(
        ..., description="Set of rolled-up tags associated with the dataset"
    )


class DatasetsGet(DatasetGet):
    data_product_links: Annotated[
        list[DataProductLink],
        Field(
            exclude=True,
            description="Links to data products associated with the dataset",
        ),
    ]
    rolled_up_tags: Annotated[
        set[Tag],
        Field(
            exclude=True,
            description="Set of rolled-up tags associated with the dataset",
        ),
    ] = Field(set(), description="Set of rolled-up tags associated with the dataset")
    about: Optional[str] = Field(
        None, exclude=True, description="Additional information about the dataset"
    )

    @computed_field
    def data_product_count(self) -> int:
        accepted_product_links = [
            link
            for link in self.data_product_links
            if link.status == DataProductDatasetLinkStatus.APPROVED
        ]
        return len(accepted_product_links)
