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


class CoderPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "CoderPlugin"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="Coder",
        icon_name="coder-logo.svg",
        platform_key="coder",
        parent_platform=None,
        has_environments=False,
        detailed_name="Coder",
        show_in_form=False,
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        data_product = db.get(DataProductModel, id)
        repo_url = (
            f"https://github.com/{settings.CODER_GITHUB_ORG}/{data_product.namespace}"
        )
        return f"{settings.CODER_BASE_URL}/templates/vscode/workspace?param.git_repo={repo_url}"
