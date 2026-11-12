from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.technical_asset_configuration.base_model import BaseTechnicalAssetConfiguration

NAME = "AzureKeyVaultTechnicalAssetConfiguration"


class AzureKeyVaultTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "azure_keyvault_technical_asset_configurations"
    __table_args__ = (
        UniqueConstraint("vault_name", name="uq_azure_keyvault_vault_name"),
    )

    vault_name: Mapped[str] = mapped_column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": NAME,
    }
