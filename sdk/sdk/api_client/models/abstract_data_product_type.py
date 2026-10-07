from enum import StrEnum


class AbstractDataProductType(StrEnum):
    DATA_PRODUCTS = "data_products"
    EXPLORATIONS = "explorations"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
