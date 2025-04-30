from uuid import UUID

from app.shared.schema import ORMModel


class DomainBasic(ORMModel):
    id: UUID
    name: str
    description: str
