from typing import Annotated

from pydantic import AfterValidator, Field

from app.configuration.access_modes.model import AccessMode as AccessModeModel
from app.shared.schema import ORMModel

DEFAULT_FOR_TECHNICAL_ASSET_TYPES_DESCRIPTION = (
    "Technical asset types for which this access mode becomes the default. "
    "A type keeps its default until another access mode is made its default."
)


def _ensure_unique(technical_asset_types: list[str]) -> list[str]:
    if len(set(technical_asset_types)) != len(technical_asset_types):
        raise ValueError("Technical asset types must be unique")
    return technical_asset_types


TechnicalAssetTypes = Annotated[list[str], AfterValidator(_ensure_unique)]


class AccessModeCreate(ORMModel):
    name: str
    description: str
    technical_asset_types: TechnicalAssetTypes
    default_for_technical_asset_types: TechnicalAssetTypes = Field(
        default=[], description=DEFAULT_FOR_TECHNICAL_ASSET_TYPES_DESCRIPTION
    )

    class Meta:
        orm_model = AccessModeModel


class AccessModeUpdate(ORMModel):
    description: str
    technical_asset_types: TechnicalAssetTypes
    default_for_technical_asset_types: TechnicalAssetTypes = Field(
        default=[], description=DEFAULT_FOR_TECHNICAL_ASSET_TYPES_DESCRIPTION
    )

    class Meta:
        orm_model = AccessModeModel
