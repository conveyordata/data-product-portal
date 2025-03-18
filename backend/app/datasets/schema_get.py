from typing import Annotated, Optional
from uuid import UUID

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
    data_product: DataProductsGet


class DataOutputLink(DataOutputDatasetAssociation):
    data_output: DataOutputGet


class DatasetGet(ORMModel):
    id: UUID
    external_id: str
    name: str
    description: str
    owners: list[User]
    data_product_links: list[DataProductLink]
    lifecycle: Optional[DataProductLifeCycle]
    status: DatasetStatus
    about: Optional[str] = None
    tags: list[Tag]
    domain: Domain
    access_type: DatasetAccessType
    data_output_links: list[DataOutputLink]
    data_product_settings: list[DataProductSettingValue]
    rolled_up_tags: set[Tag] = set([])


class DatasetsGet(DatasetGet):
    data_product_links: Annotated[list[DataProductLink], Field(exclude=True)]
    rolled_up_tags: Annotated[set[Tag], Field(exclude=True)] = set()
    about: Optional[str] = Field(None, exclude=True)

    @computed_field
    def data_product_count(self) -> int:
        accepted_product_links = [
            link
            for link in self.data_product_links
            if link.status == DataProductDatasetLinkStatus.APPROVED
        ]
        return len(accepted_product_links)
