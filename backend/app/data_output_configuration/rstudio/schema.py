from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)
from app.data_products.model import DataProduct as DataProductModel
from app.users.schema import User


class RstudioPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "RstudioPlugin"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="R Studio",
        icon_name="rstudio-logo.svg",
        platform_key="rstudio",
        parent_platform=None,
        has_environments=False,
        detailed_name="R Studio - RStudio",
        show_in_form=False,
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return f"http://localhost:8787/?folder=/home/coder/workspace/products/{data_product.namespace}"
