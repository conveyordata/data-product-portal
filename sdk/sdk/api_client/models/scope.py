from enum import StrEnum


class Scope(StrEnum):
    DATASET = "dataset"
    DATA_PRODUCT = "data_product"
    DOMAIN = "domain"
    GLOBAL = "global"

    def __str__(self) -> str:
        return str(self.value)
