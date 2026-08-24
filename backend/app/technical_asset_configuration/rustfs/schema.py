from typing import ClassVar, Literal, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.data_products.model import DataProduct as DataProductModel
from app.data_products.schema import DataProduct
from app.settings import settings
from app.technical_asset_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
    UIElementMetadata,
    UIElementSelect,
    UIElementString,
)
from app.technical_asset_configuration.data_output_types import DataOutputTypes
from app.technical_asset_configuration.enums import UIElementType
from app.technical_asset_configuration.rustfs.model import (
    NAME,
)
from app.technical_asset_configuration.rustfs.model import (
    RustFSTechnicalAssetConfiguration as RustFSTechnicalAssetConfigurationModel,
)
from app.users.schema import User


class RustFSTechnicalAssetConfiguration(AssetProviderPlugin):
    """RustFS is S3-compatible, so this mirrors the S3 plugin's bucket/suffix/path
    configuration. It is a platform of its own rather than a child of AWS because it
    is self-hosted: there is no AWS account, and no AWS console to federate into.
    """

    name: ClassVar[str] = NAME
    version: ClassVar[str] = "1.0"

    bucket: str
    suffix: str = ""
    path: str
    configuration_type: Literal[DataOutputTypes.RustFSTechnicalAssetConfiguration]

    _platform_metadata = PlatformMetadata(
        display_name="RustFS",
        icon_name="rustfs-logo.svg",
        platform_key="rustfs",
        parent_platform=None,
        has_environments=False,
        result_label="Resulting path",
        result_tooltip="The path you can access through this technical asset",
        detailed_name="Path",
    )

    class Meta:
        orm_model = RustFSTechnicalAssetConfigurationModel

    def validate_configuration(self, data_product: DataProduct, db: Session):
        pass

    def on_create(self):
        pass

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        """The tile is rendered per data product, so `id` is a data product id. Link to
        that product's bucket in the RustFS console, which the provisioner names
        <prefix><namespace>.
        """
        data_product = db.get(DataProductModel, id)
        if data_product is None:
            raise ValueError(f"data product {id} not found")
        bucket = f"{settings.RUSTFS_BUCKET_PREFIX}{data_product.namespace}"
        return f"{settings.RUSTFS_CONSOLE_URL}/rustfs/console/browser/?bucket={bucket}"

    def render_template(self, template, **context):
        """Same shape as S3: {bucket}/{suffix}/{path}, dropping empty segments."""
        return "/".join(
            [
                part
                for part in super().render_template(template, **context).split("/")
                if part
            ]
        )

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        base_metadata = super().get_ui_metadata(db)
        base_metadata += [
            UIElementMetadata(
                name="bucket",
                label="Bucket",
                type=UIElementType.Select,
                required=True,
                select=UIElementSelect(options=cls.get_platform_options(db)),
            ),
            UIElementMetadata(
                name="suffix",
                label="Suffix",
                required=True,
                type=UIElementType.String,
                string=UIElementString(initial_value=""),
                hidden=True,
                use_namespace_when_not_source_aligned=True,
            ),
            UIElementMetadata(
                name="path",
                label="Path",
                type=UIElementType.String,
                tooltip="The name of the path to give write access to",
                required=True,
            ),
        ]
        return base_metadata
