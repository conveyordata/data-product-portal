from uuid import UUID

from app.data_products.schema_basic import DataProductBasic
from app.datasets.schema_basic import DatasetBasic
from app.shared.schema import ORMModel


class BaseDomainGet(ORMModel):
    id: UUID
    name: str
    description: str


class DomainGet(BaseDomainGet):
    data_products: list[DataProductBasic]
    datasets: list[DatasetBasic]


class DomainsGet(BaseDomainGet):
    data_product_count: int
    dataset_count: int
