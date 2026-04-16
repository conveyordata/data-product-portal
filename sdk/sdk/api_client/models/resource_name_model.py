from enum import Enum


class ResourceNameModel(str, Enum):
    DATA_PRODUCT = "data_product"
    DATA_PRODUCT_SETTING = "data_product_setting"
    OUTPUT_PORT = "output_port"
    OUTPUT_PORT_SETTING = "output_port_setting"
    TECHNICAL_ASSET = "technical_asset"

    def __str__(self) -> str:
        return str(self.value)
