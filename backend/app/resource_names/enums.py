from enum import Enum


class ResourceNameModel(str, Enum):
    DATA_PRODUCT = "data_product"
    TECHNICAL_ASSET = "technical_asset"
    OUTPUT_PORT = "output_port"
    DATA_PRODUCT_SETTING = "data_product_setting"
    OUTPUT_PORT_SETTING = "output_port_setting"
