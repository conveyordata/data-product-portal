from typing import Sequence

from app.data_products.schema_response import GetDataProductsResponseItem
from app.shared.schema import ORMModel


class SearchDataProductsResponseItem(GetDataProductsResponseItem):
    pass


class SearchDataProductsResponse(ORMModel):
    data_products: Sequence[SearchDataProductsResponseItem]
