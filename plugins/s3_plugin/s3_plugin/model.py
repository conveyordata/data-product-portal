"""S3 Data Output SQLAlchemy Model"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

# Import from main portal package
try:
    from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration
except ImportError as e:
    raise ImportError(
        f"Required base model from data-product-portal backend not found: {e}. "
        "This plugin must be installed in the same environment as the data-product-portal backend."
    )


class S3TechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    """
    S3 Technical Asset Configuration Model

    Stores S3-specific configuration in a dedicated table with foreign key
    to the base data_output_configurations table.
    """

    __tablename__ = "s3_technical_asset_configurations"

    bucket: Mapped[str] = mapped_column(String, nullable=True)
    suffix: Mapped[str] = mapped_column(String, nullable=True)
    path: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "S3TechnicalAssetConfiguration",
    }
