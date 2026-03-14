from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)
from app.data_products.model import DataProduct as DataProductModel
from app.users.schema import User


class AgnoPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "AgnoPlugin"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="Agno",
        icon_name="agno-logo.svg",
        platform_key="agno",
        has_environments=False,
        show_in_form=False,
        detailed_name="Agno Agent",
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return f"https://os.agno.com/chat?type=agent&id={data_product.namespace}-agent"
