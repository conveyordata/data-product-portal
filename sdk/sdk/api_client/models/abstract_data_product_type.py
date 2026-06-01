from enum import Enum


class AbstractDataProductType(str, Enum):
    DATA_PRODUCTS = "data_products"
    EXPLORATIONS = "explorations"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
