from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_products.model import DataProduct as DataProductModel
from app.settings import settings
from app.technical_asset_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)
from app.users.schema import User


class GitHubPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "GitHubPlugin"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="GitHub",
        icon_name="github-logo.svg",
        platform_key="github",
        parent_platform=None,
        has_environments=False,
        detailed_name="GitHub",
        show_in_form=False,
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        return f"https://github.com/{settings.GITHUB_ORG}/{data_product.namespace}"
