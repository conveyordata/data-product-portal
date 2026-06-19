from uuid import UUID

from app.configuration.data_product_types.schema import DataProductType
from app.data_products.status import AbstractDataProductStatus
from app.shared.schema import ORMModel


class DataProduct(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: AbstractDataProductStatus
    type: DataProductType
