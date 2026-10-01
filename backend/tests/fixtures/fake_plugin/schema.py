from typing import ClassVar, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    ConfigType,
)
from app.data_products.schema import DataProduct
from app.technical_asset_configuration.base_schema import (
    FieldDependency,
    PlatformMetadata,
    TechnicalAssetPlugin,
    UIElementMetadata,
)
from app.technical_asset_configuration.enums import UIElementType
from app.users.schema import User
from tests.fixtures.fake_plugin.model import NAME
from tests.fixtures.fake_plugin.model import (
    FakeTechnicalAssetConfiguration as FakeTechnicalAssetConfigurationModel,
)

ICON_PACKAGE = "tests.fixtures.fake_plugin"


class FakeTechnicalAssetConfiguration(TechnicalAssetPlugin):
    name: ClassVar[str] = NAME

    path: str
    granular: bool = False
    table: str = ""

    _platform_metadata = PlatformMetadata(
        display_name="Fake",
        icon_name="icon.svg",
        icon_package=ICON_PACKAGE,
        platform_key="fake",
        parent_platform="cloud",
        detailed_name="Path",
    )

    class Meta:
        orm_model = FakeTechnicalAssetConfigurationModel

    def validate_configuration(self, data_product: DataProduct, db: Session):
        pass

    def on_create(self):
        pass

    def get_configuration(self, configs: list[ConfigType]) -> Optional[ConfigType]:
        return next(iter(configs), None)

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        return [
            UIElementMetadata(
                name="path", label="Path", type=UIElementType.String, required=True
            ),
            UIElementMetadata(
                name="granular",
                label="Granular",
                type=UIElementType.Checkbox,
                required=False,
            ),
            UIElementMetadata(
                name="table",
                label="Table",
                type=UIElementType.String,
                required=False,
                depends_on=[FieldDependency(field_name="granular", value=True)],
            ),
        ]


class FakeLinkPlugin(TechnicalAssetPlugin):
    name: ClassVar[str] = "FakeLinkPlugin"

    _platform_metadata = PlatformMetadata(
        display_name="Fake link",
        icon_name="icon.svg",
        icon_package=ICON_PACKAGE,
        platform_key="fake-link",
        has_environments=False,
        detailed_name="Link",
    )

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        return f"https://example.com/{id}"
