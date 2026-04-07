from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration


class AzureBlobTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "azure_blob_technical_asset_configurations"

    storage_account: Mapped[str] = mapped_column(String, nullable=True)
    resource_group: Mapped[str] = mapped_column(String, nullable=True)
    path: Mapped[str] = mapped_column(String, nullable=True)
    container_name: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "AzureBlobTechnicalAssetConfiguration",
    }
