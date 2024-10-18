from uuid import UUID

from app.data_product_types.schema_create import DataProductTypeCreate
from app.data_products.schema import DataProduct


class DataProductType(DataProductTypeCreate):
    id: UUID
    data_products: list[DataProduct]
