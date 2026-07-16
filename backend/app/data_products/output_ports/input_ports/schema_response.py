from typing import Sequence
from uuid import UUID

from app.abstract_data_product.schema_response import AbstractDataProductInfo
from app.data_products.output_ports.input_ports.schema import InputPortBase
from app.shared.schema import ORMModel


class OutputPortInputPort(InputPortBase):
    consuming_abstract_data_product_id: UUID
    consuming_abstract_data_product: AbstractDataProductInfo


class GetInputPortsForOutputPortResponse(ORMModel):
    input_ports: Sequence[OutputPortInputPort]
