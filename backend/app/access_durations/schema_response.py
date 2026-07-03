from uuid import UUID

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.shared.schema import ORMModel


class AccessDuration(ORMModel):
    id: UUID
    abstract_data_product_type: AbstractDataProductType
    access_duration_type: AccessDurationType
    days: int | None
    is_default: bool
