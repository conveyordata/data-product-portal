from typing import Optional
from uuid import UUID

from app.abstract_data_product.schema_request import (
    RequestInputPortsForAbstractDataProductRequestItem,
)
from app.shared.schema import ORMModel


class RequestInputPortsForExplorationRequest(ORMModel):
    output_ports: list[RequestInputPortsForAbstractDataProductRequestItem]
    justification: str


class CreateExplorationRequest(ORMModel):
    name: str
    namespace: str
    description: str
    domain_id: UUID


class CreateExplorationRequestWithInputPorts(CreateExplorationRequest):
    input_ports: Optional[RequestInputPortsForExplorationRequest] = None
