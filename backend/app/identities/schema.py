from uuid import UUID

from app.shared.schema import ORMModel


class Identity(ORMModel):
    id: UUID
    type: str
    external_id: str
