from uuid import UUID

from app.data_product_types.schema import DataProductType
from app.data_products.status import DataProductStatus
from app.shared.schema import ORMModel


class DataProduct(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    status: DataProductStatus
    type: DataProductType
