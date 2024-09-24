from uuid import UUID

from app.shared.schema import ORMModel


class Platform(ORMModel):
    id: UUID
    name: str
