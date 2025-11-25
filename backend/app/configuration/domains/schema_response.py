from typing import Sequence
from uuid import UUID

from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset
from app.shared.schema import ORMModel


class BaseDomainGet(ORMModel):
    id: UUID
    name: str
    description: str


class DomainGet(BaseDomainGet):
    data_products: list[DataProduct]
    datasets: list[Dataset]


class DomainsGetItem(BaseDomainGet):
    data_product_count: int
    dataset_count: int


class DomainsGet(ORMModel):
    domains: Sequence[DomainsGetItem]


class CreateDomainResponse(ORMModel):
    id: UUID


class UpdateDomainResponse(ORMModel):
    id: UUID
