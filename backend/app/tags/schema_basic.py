from uuid import UUID

from app.shared.schema import ORMModel


class TagBasic(ORMModel):
    id: UUID
    value: str

    class Config:
        frozen = True
