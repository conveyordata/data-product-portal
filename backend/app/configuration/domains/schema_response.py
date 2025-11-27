from typing import Sequence
from uuid import UUID
from warnings import deprecated

from app.data_products.schema import DataProduct
from app.datasets.schema import Dataset, OutputPort
from app.shared.schema import ORMModel


class BaseDomainGet(ORMModel):
    id: UUID
    name: str
    description: str


@deprecated("Use DomainGetResponse instead")
class DomainGetOld(BaseDomainGet):
    data_products: list[DataProduct]
    datasets: list[Dataset]


class GetDomainResponse(BaseDomainGet):
    data_products: list[DataProduct]
    output_ports: list[OutputPort]

    @classmethod
    def from_domain_get_old(cls, d: DomainGetOld) -> "GetDomainResponse":
        return GetDomainResponse(
            id=d.id,
            name=d.name,
            description=d.description,
            data_products=d.data_products,
            output_ports=d.datasets,
        )


@deprecated("Use GetDomainsItem instead")
class GetDomainsItemOld(BaseDomainGet):
    data_product_count: int
    dataset_count: int


class GetDomainsItem(BaseDomainGet):
    data_product_count: int
    output_port_count: int

    @classmethod
    def from_get_domains_item_old(cls, d: GetDomainsItemOld) -> "GetDomainsItem":
        return GetDomainsItem(
            id=d.id,
            name=d.name,
            description=d.description,
            data_product_count=d.data_product_count,
            output_port_count=d.dataset_count,
        )


class GetDomainsResponse(ORMModel):
    domains: Sequence[GetDomainsItem]


class CreateDomainResponse(ORMModel):
    id: UUID


class UpdateDomainResponse(ORMModel):
    id: UUID
