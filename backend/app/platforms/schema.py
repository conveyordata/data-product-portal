from uuid import UUID

from app.shared.schema import ORMModel


class PlatformCreate(ORMModel):
    name: str


class Platform(PlatformCreate):
    id: UUID
