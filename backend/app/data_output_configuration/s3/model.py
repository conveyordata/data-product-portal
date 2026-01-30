from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration


class S3TechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "s3_technical_asset_configurations"

    bucket: Mapped[str] = mapped_column(String, nullable=True)
    suffix: Mapped[str] = mapped_column(String, nullable=True)
    path: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "S3TechnicalAssetConfiguration",
    }
