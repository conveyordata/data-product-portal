from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)
from app.data_products.model import DataProduct as DataProductModel
from app.users.schema import User


class QuartoPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "QuartoPlatform"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="Quarto",
        icon_name="quarto-logo.svg",
        platform_key="quarto",
        parent_platform=None,
        has_environments=False,
        detailed_name="Quarto - Documentation",
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return f"http://localhost:8888/docs/{data_product.namespace}"
