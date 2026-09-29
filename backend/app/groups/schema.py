from uuid import UUID

from app.shared.schema import ORMModel


class Group(ORMModel):
    id: UUID
    external_id: str
    display_name: str
