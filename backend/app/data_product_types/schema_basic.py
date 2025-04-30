from uuid import UUID

from app.data_product_types.enums import DataProductIconKey
from app.shared.schema import ORMModel


class DataProductTypeBasic(ORMModel):
    id: UUID
    name: str
    description: str
    icon_key: DataProductIconKey
