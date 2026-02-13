from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)
from app.data_products.model import DataProduct as DataProductModel
from app.users.schema import User


class CoderPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "CoderPlatform"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="VS Code",
        icon_name="coder-logo.svg",
        platform_key="coder",
        parent_platform=None,
        has_environments=False,
        detailed_name="VS Code - Coder",
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return f"http://localhost:8443/?folder=/home/coder/workspace/products/{data_product.namespace}"

    @classmethod
    def only_tile(cls) -> bool:
        """Conveyor is currently only shown as a tile in the UI, as it doesn't have technical assets or detailed configuration options."""
        return True
