from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.technical_asset_configuration.base_model import BaseTechnicalAssetConfiguration

NAME = "FakeTechnicalAssetConfiguration"


class FakeTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "fake_technical_asset_configurations"

    path: Mapped[str] = mapped_column(String, nullable=True)
    granular: Mapped[bool] = mapped_column(Boolean, nullable=True)
    table: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": NAME,
    }
