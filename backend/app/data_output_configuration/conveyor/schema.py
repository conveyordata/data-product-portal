from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.conveyor.notebook_builder import CONVEYOR_SERVICE
from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)
from app.data_products.model import DataProduct as DataProductModel
from app.users.schema import User


class ConveyorPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "ConveyorPlatform"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="Conveyor",
        icon_name="conveyor-logo.svg",
        platform_key="conveyor",
        parent_platform=None,
        has_environments=False,
        detailed_name="Conveyor",
        show_in_form=False,
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return CONVEYOR_SERVICE.generate_ide_url(data_product.namespace)
