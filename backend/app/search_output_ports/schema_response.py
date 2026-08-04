from typing import Sequence

from app.data_products.output_ports.schema_response import BaseOutputPortGet
from app.shared.schema import ORMModel


class SearchOutputPortsResponseItem(BaseOutputPortGet):
    abstract_data_product_count: int
    technical_assets_count: int
    data_product_name: str


class SearchOutputPortsResponse(ORMModel):
    output_ports: Sequence[SearchOutputPortsResponseItem]
