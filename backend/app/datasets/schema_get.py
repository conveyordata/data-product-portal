from typing import List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field, computed_field

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


class DatasetGet(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the dataset")
    external_id: str = Field(..., description="External identifier for the dataset")
    name: str = Field(..., description="Name of the dataset")
    description: str = Field(..., description="Description of the dataset")
    owners: List[User] = Field(..., description="List of users who own the dataset")
    data_product_links: List[DataProductLink] = Field(
        ..., description="Links to data products associated with the dataset"
    )
    lifecycle: Optional[DataProductLifeCycle] = Field(
        None, description="Lifecycle status of the dataset"
    )
    status: DatasetStatus = Field(..., description="Current status of the dataset")
    about: Optional[str] = Field(
        None, description="Additional information about the dataset"
    )
    tags: List[Tag] = Field(..., description="List of tags associated with the dataset")
    domain: Domain = Field(..., description="Domain to which the dataset belongs")
    access_type: DatasetAccessType = Field(
        ..., description="Access type of the dataset"
    )
    data_output_links: List[DataOutputLink] = Field(
        ..., description="Links to data outputs associated with the dataset"
    )
    data_product_settings: List[DataProductSettingValue] = Field(
        ..., description="Settings for the data product"
    )
    rolled_up_tags: Set[Tag] = Field(
        ..., description="Set of rolled-up tags associated with the dataset"
    )


class DatasetsGet(DatasetGet):
    data_product_links: List[DataProductLink] = Field(
        ..., description="Links to data products associated with the dataset"
    )
    rolled_up_tags: Set[Tag] = Field(
        ..., description="Set of rolled-up tags associated with the dataset"
    )
    about: Optional[str] = Field(
        None, description="Additional information about the dataset"
    )

    @computed_field
    def data_product_count(self) -> int:
        accepted_product_links = [
            link
            for link in self.data_product_links
            if link.status == DataProductDatasetLinkStatus.APPROVED
        ]
        return len(accepted_product_links)
