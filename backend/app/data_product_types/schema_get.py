from app.data_product_types.schema import DataProductType
from app.data_products.schema import DataProduct


class DataProductTypeGet(DataProductType):
    data_products: list[DataProduct]


class DataProductTypesGet(DataProductType):
    data_product_count: int
