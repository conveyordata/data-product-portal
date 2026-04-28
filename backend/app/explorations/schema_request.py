from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel


class RequestInputPortsForExplorationRequest(ORMModel):
    output_ports: list[UUID]
    justification: str


class CreateExplorationRequest(ORMModel):
    name: str
    namespace: Optional[str] = None
    description: str
    domain_id: UUID


class CreateExplorationRequestWithInputPorts(CreateExplorationRequest):
    input_ports: Optional[RequestInputPortsForExplorationRequest] = None
