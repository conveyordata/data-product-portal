from enum import UNIQUE, Enum, verify


@verify(UNIQUE)
class AbstractDataProductType(str, Enum):
    UNKNOWN = "unknown"
    DATA_PRODUCT = "data_products"
    EXPLORATION = "explorations"
