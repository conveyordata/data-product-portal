from app.configuration.access_modes.model import AccessMode as AccessModeModel
from app.shared.schema import ORMModel


class AccessModeCreate(ORMModel):
    name: str
    description: str
    technical_asset_types: list[str]

    class Meta:
        orm_model = AccessModeModel


class AccessModeUpdate(ORMModel):
    description: str
    technical_asset_types: list[str]

    class Meta:
        orm_model = AccessModeModel
