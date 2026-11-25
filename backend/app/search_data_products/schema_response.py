from typing import Optional, Sequence
from uuid import UUID

from pydantic import AliasChoices, Field

from app.configuration.access_modes.schema_response import AccessMode
from app.configuration.data_product_lifecycles.schema import DataProductLifeCycle
from app.configuration.data_product_types.schema import DataProductType
from app.configuration.domains.schema import Domain
from app.configuration.tags.schema import Tag
from app.shared.schema import ORMModel


class SearchDataProductsOutputPort(ORMModel):
    id: UUID
    name: str
    description: str
    access_modes: list[AccessMode]


class SearchDataProductsResponseItem(ORMModel):
    id: UUID
    name: str
    description: str
    tags: list[Tag]
    domain: Domain
    type: DataProductType
    lifecycle: Optional[DataProductLifeCycle]
    output_ports: Sequence[SearchDataProductsOutputPort] = Field(
        validation_alias=AliasChoices("output_ports", "datasets")
    )
    consumer_count: int


class SearchDataProductsResponse(ORMModel):
    data_products: Sequence[SearchDataProductsResponseItem]
