from typing import Sequence
from uuid import UUID

from app.configuration.domains.schema import Domain
from app.shared.schema import ORMModel


class Exploration(ORMModel):
    id: UUID
    name: str
    namespace: str
    description: str
    domain: Domain


class CreateExplorationResponse(Exploration):
    pass


class GetExplorationsResponse(ORMModel):
    explorations: Sequence[Exploration]


class LinkInputPortsToExplorationResponse(ORMModel):
    input_port_links: list[UUID]
