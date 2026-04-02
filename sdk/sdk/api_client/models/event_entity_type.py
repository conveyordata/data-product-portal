from enum import Enum


class EventEntityType(str, Enum):
    DATA_PRODUCT = "data_product"
    OUTPUT_PORT = "output_port"
    TECHNICAL_ASSET = "technical_asset"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
