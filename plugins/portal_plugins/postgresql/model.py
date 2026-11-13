from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.technical_asset_configuration.base_model import (
    BaseTechnicalAssetConfiguration,
    BaseTechnicalAssetEnvironmentConfiguration,
)

NAME = "PostgreSQLTechnicalAssetConfiguration"


class PostgreSQLTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "postgresql_technical_asset_configurations"

    database: Mapped[str] = mapped_column(String, nullable=True)
    schema: Mapped[str] = mapped_column(String, nullable=True)
    table: Mapped[str] = mapped_column(String, nullable=True)
    access_granularity: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": NAME,
    }


class PostgreSQLEnvironmentConfiguration(BaseTechnicalAssetEnvironmentConfiguration):
    __tablename__ = "postgresql_environment_configurations"

    engine_version: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[str] = mapped_column(String, nullable=False)
    storage_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    instance_name: Mapped[str] = mapped_column(String, nullable=False)
