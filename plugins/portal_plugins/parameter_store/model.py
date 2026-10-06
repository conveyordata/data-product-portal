from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.technical_asset_configuration.base_model import BaseTechnicalAssetConfiguration

NAME = "ParameterStoreTechnicalAssetConfiguration"


class ParameterStoreTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "parameter_store_technical_asset_configurations"

    prefix: Mapped[str] = mapped_column(String, nullable=True)
    parameter_name: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": NAME,
    }
