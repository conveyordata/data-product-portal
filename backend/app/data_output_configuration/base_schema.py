from abc import ABC
from enum import Enum
from typing import Any, ClassVar, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuration.environments.platform_service_configurations.schema_response import (
    ConfigType,
)
from app.configuration.platforms.platform_services.model import (
    PlatformService as PlatformServiceModel,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.platform_service_configurations.model import (
    PlatformServiceConfiguration as PlatformServiceConfigurationModel,
)
from app.platform_service_configurations.schema import PlatformServiceConfiguration
from app.shared.schema import ORMModel


class UIElementType(str, Enum):
    String = "string"
    Select = "select"
    Checkbox = "checkbox"


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


class UIElementMetadata(ORMModel):
    label: str  # The label shown in the UI, passed through a translating layer
    type: UIElementType  # The type of UI element
    required: bool  # Whether this field is required to be filled in in the form
    name: str  # The internal name of the field, used as key in the configuration
    tooltip: Optional[str] = (
        None  # Tooltip text shown in the UI, passed through a translating layer
    )
    hidden: Optional[bool] = (
        None  # Whether this field is hidden in the UI, used to pass generated values without user input.
    )
    initial_value: Optional[str | bool] = (
        None  # Initial value for the field in the UI, select fields can't have an initial value yet.
    )
    value_prop_name: Optional[str] = (
        None  # Used to override the default value_prop_name if needed, e.g. checked for checkboxes
    )
    depends_on: Optional[FieldDependency] = (
        None  # Conditional rendering based on another field's value in the form.
    )
    max_count: Optional[int] = None  # For selects the maximum number of items allowed
    disabled: Optional[bool] = (
        None  # Whether this field is disabled in the UI, useful to show generated values
    )
    use_namespace_when_not_source_aligned: Optional[bool] = (
        None  # Whether to use the data product namespace as default value when the data product is not source aligned
    )
    options: Optional[List[SelectOption]] = None  # Additional options for select fields


class UIElementCheckbox(UIElementMetadata):
    type: UIElementType = UIElementType.Checkbox
    value_prop_name: str = "checked"


class UIElementSelect(UIElementMetadata):
    type: UIElementType = UIElementType.Select
    max_count: Optional[int] = 1


class UIElementString(UIElementMetadata):
    type: UIElementType = UIElementType.String


class PlatformMetadata(ORMModel):
    """Metadata describing how a platform should be displayed in the UI"""

    display_name: str
    icon_name: str
    platform_key: str
    parent_platform: Optional[str] = None
    result_label: str = "Resulting output"
    result_tooltip: str = "The output you can access through this technical asset"


class AssetProviderPlugin(ORMModel, ABC):
    """Base class for all data output provider plugins"""

    name: ClassVar[str]
    version: ClassVar[str] = "1.0"
    configuration_type: DataOutputTypes

    # Platform metadata - should be overridden in subclasses
    _platform_metadata: ClassVar[Optional[PlatformMetadata]] = None

    def render_template(self, template: str, **context) -> str:
        """Render a template with configuration values"""
        return template.format(**self.model_dump(), **context)

    def get_configuration(self, configs: list[ConfigType]) -> Optional[ConfigType]:
        """Get platform and environment specific configuration"""
        raise NotImplementedError

    def validate(self) -> None:
        """Validate the configuration (e.g., no illegal names in identifiers)"""
        pass

    @classmethod
    def get_platform_options(cls, db: Session) -> List[SelectOption]:
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
    def get_ui_metadata(cls, db: Session) -> List[UIElementMetadata]:
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
    def get_logo(cls) -> str:
        """Get the logo filename for this plugin"""
        platform_meta = cls.get_platform_metadata()
        return platform_meta.icon_name

    def get_url(self, environment: str) -> Optional[str]:
        """Get the URL for accessing this resource in the given environment"""
        return None

    @classmethod
    def has_environnments(cls) -> bool:
        """Whether this plugin supports multiple environments"""
        return True
