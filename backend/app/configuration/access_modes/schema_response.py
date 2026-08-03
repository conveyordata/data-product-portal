from uuid import UUID

from app.configuration.access_modes.model import AccessMode as AccessModeModel
from app.shared.schema import ORMModel


class AccessMode(ORMModel):
    id: UUID
    name: str
    description: str

    class Meta:
        orm_model = AccessModeModel


class GetAccessModes(ORMModel):
    access_modes: list[AccessMode]
