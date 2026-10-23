from abc import ABC
from base64 import b64encode
from functools import cache
from importlib import resources
from typing import TYPE_CHECKING, Any, ClassVar, Optional
from uuid import UUID

from pydantic import computed_field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.configuration.domains.schema import Domain
from app.configuration.platforms.model import PlatformEnvironmentSettings
from app.core.logging import logger
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.enums import TechnicalMapping
from app.shared.schema import ORMModel
from app.technical_asset_configuration.enums import UIElementType

if TYPE_CHECKING:
    from app.data_products.model import DataProduct as DataProductModel
    from app.plugins.platform import Platform


@cache
def icon_data_uri(package: Optional[str], name: str) -> Optional[str]:
    if not package:
        return None
    try:
        icon = resources.files(package).joinpath(name).read_bytes()
    except Exception:
        logger.exception(f"No readable icon at {package}/{name}")
        return None
    return f"data:image/svg+xml;base64,{b64encode(icon).decode()}"


class FieldDependency(ORMModel):
    """Represents a field dependency for conditional visibility.
    e.g. if field A has depends_on(field_name=B, value=Y), then field A is only shown when field B has value Y
    In practice this is often used with checkbox fields having value=True
    """

    field_name: str
    value: Any


class SelectOption(ORMModel):
    """Option for select UI elements"""

    label: str
    value: str | bool


class UIElementCheckbox(ORMModel):
    initial_value: Optional[bool] = None


class UIElementRadio(ORMModel):
    max_count: Optional[int] = 1
    initial_value: Optional[str] = None
    options: Optional[list[SelectOption]] = None  # Additional options for radio fields


class UIElementSelect(ORMModel):
    max_count: Optional[int] = 1
    options: Optional[list[SelectOption]] = None  # Additional options for select fields


class UIElementString(ORMModel):
    initial_value: Optional[str] = None


class UIElementMetadata(ORMModel):
    label: str  # The label shown in the UI
    type: UIElementType  # The type of UI element
    required: bool  # Whether this field is required to be filled in in the form
    name: str  # The internal name of the field, used as key in the configuration
    tooltip: Optional[str] = None  # Tooltip text shown in the UI
    hidden: Optional[bool] = (
        None  # Whether this field is hidden in the UI, used to pass generated values without user input.
    )
    checkbox: Optional[UIElementCheckbox] = None
    select: Optional[UIElementSelect] = None
    string: Optional[UIElementString] = None
    radio: Optional[UIElementRadio] = None
    depends_on: Optional[list[FieldDependency]] = (
        None  # Conditional rendering based on another field's value in the form.
    )
    disabled: Optional[bool] = (
        None  # Whether this field is disabled in the UI, useful to show generated values
    )
    use_namespace_when_not_source_aligned: Optional[bool] = (
        None  # Whether to use the data product namespace as default value when the data product is not source aligned
    )

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.type == UIElementType.Radio and self.radio is None:
            self.radio = UIElementRadio()
        if self.type == UIElementType.Select and self.select is None:
            self.select = UIElementSelect()
        if self.type == UIElementType.String and self.string is None:
            self.string = UIElementString()
        if self.type == UIElementType.Checkbox and self.checkbox is None:
            self.checkbox = UIElementCheckbox()


class PlatformMetadata(ORMModel):
    """Metadata describing how a platform should be displayed in the UI"""

    display_name: str
    icon_name: str
    icon_package: Optional[str] = None
    platform_key: str
    result_label: str = "Resulting output"
    result_tooltip: str = "The output you can access through this technical asset"
    detailed_name: str
    shareable: bool = True
    result_string_template: Optional[str] = None
    technical_info_template: Optional[str] = None


class TechnicalAssetContext(ORMModel):
    id: Optional[UUID] = None
    namespace: str
    technical_mapping: TechnicalMapping


class PluginContext(ORMModel):
    technical_asset: TechnicalAssetContext
    data_product: DataProduct
    domain: Domain

    @classmethod
    def build(
        cls,
        data_product: "DataProductModel",
        namespace: str,
        technical_mapping: TechnicalMapping,
        technical_asset_id: Optional[UUID] = None,
    ) -> "PluginContext":
        return cls(
            technical_asset=TechnicalAssetContext(
                id=technical_asset_id,
                namespace=namespace,
                technical_mapping=technical_mapping,
            ),
            data_product=DataProduct.model_validate(data_product),
            domain=Domain.model_validate(data_product.domain),
        )


class TechnicalAssetPlugin(ORMModel, ABC):
    version: ClassVar[str] = "1.0"
    mcp_instructions: ClassVar[str] = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name(self) -> str:
        raise NotImplementedError

    _platform_metadata: ClassVar[Optional[PlatformMetadata]] = None
    platform: ClassVar[type["Platform"]]

    def render_template(
        self, template: str, *, plugin_context: PluginContext, **context: Any
    ) -> str:
        return template.format(
            **{**dict(plugin_context), **self.model_dump(), **context}
        )

    def get_configuration(self, configs: list[Any]) -> Optional[Any]:
        raise NotImplementedError

    def validate_configuration(self, context: PluginContext, db: Session) -> None:
        """Raise when the configuration isn't acceptable, on create with the default technical mapping."""

    @classmethod
    def settings_field(cls) -> str:
        return cls.get_platform_metadata().platform_key.replace("-", "_")

    @classmethod
    def get_platform_options(cls, db: Session) -> list[SelectOption]:
        identifiers = {
            entry["identifier"]
            for settings in db.scalars(
                select(PlatformEnvironmentSettings.settings).filter_by(
                    platform_key=cls.platform.key
                )
            )
            for entry in settings.get(cls.settings_field(), [])
        }
        return [
            SelectOption(label=identifier, value=identifier)
            for identifier in sorted(identifiers)
        ]

    @classmethod
    def get_ui_metadata(cls, db: Session) -> list[UIElementMetadata]:
        """Returns the UI metadata for form generation"""
        return []

    @classmethod
    def get_platform_metadata(cls) -> PlatformMetadata:
        """Returns platform display metadata"""
        if cls._platform_metadata is None:
            # Fallback to auto-generation from class name
            class_name = cls.__name__
            platform_key = class_name.lower().replace("dataoutput", "")
            return PlatformMetadata(
                display_name=class_name.replace("DataOutput", ""),
                icon_name=f"{platform_key}-logo.svg",
                platform_key=platform_key,
                detailed_name=class_name,
            )
        return cls._platform_metadata

    @classmethod
    def get_icon_data_uri(cls) -> Optional[str]:
        platform_meta = cls.get_platform_metadata()
        return icon_data_uri(platform_meta.icon_package, platform_meta.icon_name)

    @classmethod
    def get_logo(cls) -> str:
        """Get the logo filename for this plugin"""
        platform_meta = cls.get_platform_metadata()
        return platform_meta.icon_name

    @classmethod
    def register_mcp_tools(cls, mcp: Any) -> None:
        """Register MCP tools for this plugin. Override in subclasses that support MCP querying."""
