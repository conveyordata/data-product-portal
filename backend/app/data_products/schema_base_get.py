from typing import Optional
from uuid import UUID

from app.data_product_types.schema_create import DataProductTypeCreate
from app.data_products.status import DataProductStatus
from app.domains.schema import Domain
from app.shared.schema import ORMModel


class BaseDataProductGet(ORMModel):
    id: UUID
    name: str
    description: str
    about: Optional[str]
    namespace: str
    status: DataProductStatus
    type: DataProductTypeCreate
    domain: Domain
