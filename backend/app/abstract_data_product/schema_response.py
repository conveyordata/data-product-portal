from app.abstract_data_product.model import AbstractDataProductType
from app.shared.schema import ORMModel


class AbstractDataProductInfo(ORMModel):
    name: str
    namespace: str
    abstract_data_product_type: AbstractDataProductType
