from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration


class PostgreSQLTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "postgresql_technical_asset_configurations"

    database: Mapped[str] = mapped_column(String, nullable=True)
    schema: Mapped[str] = mapped_column(String, nullable=True)
    table: Mapped[str] = mapped_column(String, nullable=True)
    access_granularity: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "PostgreSQLTechnicalAssetConfiguration",
    }
