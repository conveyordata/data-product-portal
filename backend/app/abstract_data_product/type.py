from enum import Enum


class AbstractDataProductType(str, Enum):
    UNKNOWN = "unknown"
    DATA_PRODUCT = "data_products"
    EXPLORATION = "explorations"
