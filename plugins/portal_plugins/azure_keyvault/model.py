from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.technical_asset_configuration.base_model import BaseTechnicalAssetConfiguration

NAME = "AzureKeyVaultTechnicalAssetConfiguration"


class AzureKeyVaultTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "azure_keyvault_technical_asset_configurations"

    vault_name: Mapped[str] = mapped_column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": NAME,
    }
