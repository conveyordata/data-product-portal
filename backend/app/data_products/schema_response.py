from typing import Optional
from uuid import UUID

from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_settings.schema import DataProductSettingValue
from app.configuration.data_product_types.schema import DataProductType
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.data_outputs.schema_response import BaseDataOutputGet
from app.data_outputs_datasets.schema_response import (
    BaseDataOutputDatasetAssociationGet,
)
from app.data_products.status import DataProductStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    namespace: str
    status: DataProductStatus

    # Nested schemas
    tags: list[Tag]
    usage: Optional[str]
    domain: Domain
    type: DataProductType
    lifecycle: Optional[DataProductLifeCycle]
    data_product_settings: list[DataProductSettingValue]


class DataOutputLinks(BaseDataOutputGet):
    # Nested schemas
    dataset_links: list[BaseDataOutputDatasetAssociationGet]


class DatasetLinks(DataProductDatasetAssociation):
    # Nested schemas
    dataset: Dataset


class DataProductGet(BaseDataProductGet):
    about: Optional[str]

    # Nested schemas
    dataset_links: list[DatasetLinks]
    data_outputs: list[DataOutputLinks]
    datasets: list[Dataset]
    rolled_up_tags: set[Tag]


class DataProductsGet(BaseDataProductGet):
    user_count: int
    dataset_count: int
    data_outputs_count: int


class LinkDatasetsToDataProductPost(ORMModel):
    dataset_links: list[UUID]
