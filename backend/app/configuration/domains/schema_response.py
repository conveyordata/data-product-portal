from typing import Sequence
from uuid import UUID

from app.configuration.environments.schema_response import EnvironmentGetItem
from app.shared.schema import ORMModel


class BaseDomainGet(ORMModel):
    id: UUID
    name: str
    description: str
    environments: Sequence[EnvironmentGetItem]


class GetDomainResponse(BaseDomainGet):
    pass


class GetDomainsItem(BaseDomainGet):
    abstract_data_product_count: int


class GetDomainsResponse(ORMModel):
    domains: Sequence[GetDomainsItem]


class CreateDomainResponse(ORMModel):
    id: UUID


class UpdateDomainResponse(ORMModel):
    id: UUID
