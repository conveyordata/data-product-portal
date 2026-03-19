from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.data_output_configuration.base_model import BaseTechnicalAssetConfiguration


class OSISemanticModelTechnicalAssetConfiguration(BaseTechnicalAssetConfiguration):
    __tablename__ = "osi_semantic_model_technical_asset_configurations"

    model_name: Mapped[str] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "OSISemanticModelTechnicalAssetConfiguration",
    }
