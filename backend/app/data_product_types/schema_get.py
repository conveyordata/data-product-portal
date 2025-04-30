from uuid import UUID

from app.data_product_types.enums import DataProductIconKey
from app.data_products.schema_basic import DataProductBasic
from app.shared.schema import ORMModel


class BaseDataProductTypeGet(ORMModel):
    id: UUID
    name: str
    description: str
    icon_key: DataProductIconKey


class DataProductTypeGet(BaseDataProductTypeGet):
    data_products: list[DataProductBasic]


class DataProductTypesGet(BaseDataProductTypeGet):
    data_product_count: int
