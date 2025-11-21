from typing import Sequence
from uuid import UUID

from app.configuration.data_product_types.enums import DataProductIconKey
from app.data_products.schema import DataProduct
from app.shared.schema import ORMModel


class BaseDataProductTypeGet(ORMModel):
    id: UUID
    name: str
    description: str
    icon_key: DataProductIconKey


class DataProductTypeGet(BaseDataProductTypeGet):
    data_products: list[DataProduct]


class DataProductTypesGetItem(BaseDataProductTypeGet):
    data_product_count: int


class DataProductTypesGet(ORMModel):
    data_product_types: Sequence[DataProductTypesGetItem]
