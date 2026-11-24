from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.technical_asset_configuration.base_model import (
    BaseTechnicalAssetConfiguration,
    BaseTechnicalAssetEnvironmentConfiguration,
)

NAME = "SizingTechnicalAssetConfiguration"


class SizingTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "sizing_technical_asset_configurations"

    path: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": NAME,
    }


class SizingConfiguration(BaseTechnicalAssetEnvironmentConfiguration):
    __tablename__ = "sizing_configurations"

    size: Mapped[str] = mapped_column(String, nullable=False)
    replicas: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
