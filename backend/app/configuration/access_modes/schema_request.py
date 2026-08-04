from app.configuration.access_modes.model import AccessMode as AccessModeModel
from app.shared.schema import ORMModel


class AccessModeCreate(ORMModel):
    name: str
    description: str

    class Meta:
        orm_model = AccessModeModel


class AccessModeUpdate(ORMModel):
    description: str

    class Meta:
        orm_model = AccessModeModel
