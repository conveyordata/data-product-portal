from abc import ABC
from base64 import b64encode
from functools import cache
from importlib import resources
from typing import Any, ClassVar, Optional
from uuid import UUID

from pydantic import computed_field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    ConfigType,
)
from app.configuration.platform_service_configurations.model import (
    PlatformServiceConfiguration as PlatformServiceConfigurationModel,
)
from app.configuration.platform_service_configurations.schema import (
    PlatformServiceConfiguration,
)
from app.configuration.platforms.platform_services.model import (
    PlatformService as PlatformServiceModel,
)
from app.core.logging import logger
from app.shared.schema import ORMModel
from app.technical_asset_configuration.enums import UIElementType
from app.users.schema import User


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
    has_environments: bool = True
    parent_platform: Optional[str] = None
    result_label: str = "Resulting output"
    result_tooltip: str = "The output you can access through this technical asset"
    detailed_name: str
    show_in_form: bool = True


class TechnicalAssetPlugin(ORMModel, ABC):
    version: ClassVar[str] = "1.0"
    mcp_instructions: ClassVar[str] = ""
    target_revision: ClassVar[Optional[str]] = None
    migrations_package: ClassVar[Optional[str]] = None
    result_string_template: ClassVar[Optional[str]] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name(self) -> str:
        raise NotImplementedError

    _platform_metadata: ClassVar[Optional[PlatformMetadata]] = None

    def render_template(self, template: str, **context: dict[str, Any]) -> str:
        return template.format(**self.model_dump(), **context)

    def get_configuration(self, configs: list[ConfigType]) -> Optional[ConfigType]:
        raise NotImplementedError

    @classmethod
    def get_url(
        cls, id: UUID, db: Session, actor: User, environment: Optional[str] = None
    ) -> str:
        """Get the URL to the access tiles."""
        raise NotImplementedError

    @classmethod
    def get_platform_options(cls, db: Session) -> list[SelectOption]:
        """Get platform specific options from the database if needed"""
        if not cls._platform_metadata:
            raise NotImplementedError("Platform metadata not defined for this plugin")

        service = db.scalar(
            select(PlatformServiceModel).where(
                func.lower(PlatformServiceModel.name)
                == cls._platform_metadata.platform_key
            )
        )
        if not service:
            raise NotImplementedError("No platform service found")
        config = db.scalar(
            select(PlatformServiceConfigurationModel).filter_by(service_id=service.id)
        )
        if not config:
            raise NotImplementedError("No platform service configuration found")
        return [
            SelectOption(label=option, value=option)
            for option in PlatformServiceConfiguration.model_validate(config).config
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
            )
        return cls._platform_metadata

    @classmethod
    @cache
    def get_icon_data_uri(cls) -> Optional[str]:
        platform_meta = cls.get_platform_metadata()
        if not platform_meta.icon_package:
            return None
        try:
            icon = (
                resources.files(platform_meta.icon_package)
                .joinpath(platform_meta.icon_name)
                .read_bytes()
            )
        except Exception:
            logger.exception(
                f"Plugin '{cls.name}' has no readable icon at "
                f"{platform_meta.icon_package}/{platform_meta.icon_name}"
            )
            return None
        return f"data:image/svg+xml;base64,{b64encode(icon).decode()}"

    @classmethod
    def get_logo(cls) -> str:
        """Get the logo filename for this plugin"""
        platform_meta = cls.get_platform_metadata()
        return platform_meta.icon_name

    @classmethod
    def register_mcp_tools(cls, mcp: Any) -> None:
        """Register MCP tools for this plugin. Override in subclasses that support MCP querying."""
