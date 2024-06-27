from typing import Annotated, Optional
from uuid import UUID

from pydantic import computed_field, Field

from app.business_areas.schema import BusinessArea
from app.data_products.schema_get import DataProductsGet
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.shared.schema import ORMModel
from app.tags.schema import Tag
from app.users.schema import User


class DataProductLink(DataProductDatasetAssociation):
    data_product: DataProductsGet


class DatasetGet(ORMModel):
    id: UUID
    external_id: str
    name: str
    description: str
    owners: list[User]
    data_product_links: list[DataProductLink]
    status: DatasetStatus
    about: Optional[str] = None
    tags: list[Tag]
    business_area: BusinessArea
    access_type: DatasetAccessType


class DatasetsGet(DatasetGet):
    data_product_links: Annotated[list[DataProductLink], Field(exclude=True)]
    about: Optional[str] = Field(None, exclude=True)

    @computed_field
    def data_product_count(self) -> int:
        accepted_product_links = [
            link
            for link in self.data_product_links
            if link.status == DataProductDatasetLinkStatus.APPROVED
        ]
        return len(accepted_product_links)
