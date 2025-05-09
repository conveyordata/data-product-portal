from uuid import UUID

from app.shared.schema import ORMModel


class Tag(ORMModel):
    id: UUID
    value: str

    class Config:
        frozen = True
