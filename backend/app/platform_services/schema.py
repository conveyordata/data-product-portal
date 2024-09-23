from uuid import UUID

from app.platforms.schema import Platform
from app.shared.schema import ORMModel


class PlatformService(ORMModel):
    id: UUID
    name: str
    platform: Platform
