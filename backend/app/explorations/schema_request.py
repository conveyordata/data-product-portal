from uuid import UUID

from app.shared.schema import ORMModel


class CreateExplorationRequest(ORMModel):
    name: str
    namespace: str
    description: str
    domain_id: UUID
