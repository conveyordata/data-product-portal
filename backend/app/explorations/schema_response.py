from typing import Sequence
from uuid import UUID

from app.abstract_data_product.schema_response import AbstractDataProductInputPort
from app.configuration.domains.schema import Domain
from app.data_products.status import AbstractDataProductStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class Exploration(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    domain: Domain
    status: AbstractDataProductStatus
    finalizers: list[str]


class CreateExplorationResponse(Exploration):
    pass


class GetExplorationResponse(Exploration):
    owner: User


class GetExplorationsResponse(ORMModel):
    explorations: Sequence[Exploration]


class GetExplorationInputPortsResponse(ORMModel):
    input_ports: Sequence[AbstractDataProductInputPort]


class RequestInputPortsForExplorationResponse(ORMModel):
    input_port_ids: list[UUID]


class RenewInputPortForExplorationResponse(ORMModel):
    input_port_id: UUID
