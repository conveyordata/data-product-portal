from enum import Enum


class Scope(str, Enum):
    DATASET = "dataset"
    DATA_PRODUCT = "data_product"
    DOMAIN = "domain"
    GLOBAL = "global"

    def __str__(self) -> str:
        return str(self.value)
