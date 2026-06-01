from typing import Sequence

from app.data_products.output_ports.schema_response import OutputPortsGet
from app.shared.schema import ORMModel


class SearchOutputPortsResponseItem(OutputPortsGet):
    pass


class SearchOutputPortsResponse(ORMModel):
    output_ports: Sequence[SearchOutputPortsResponseItem]
