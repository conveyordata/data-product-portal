from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType


class UpdateAccessModel:
    abstract_data_product_type: AbstractDataProductType
    access_duration_type: AccessDurationType
    days: int | None
    is_default: bool
