from abc import ABC
from enum import Enum
from typing import Any, ClassVar, List, Optional

from app.configuration.environments.platform_service_configurations.schema_response import (
    ConfigType,
)
from app.data_output_configuration.data_output_types import DataOutputTypes
from app.shared.schema import ORMModel


class UIElementType(str, Enum):
    String = "string"
    Select = "select"
    Checkbox = "checkbox"


class FieldDependency(ORMModel):
    """Represents a field dependency for conditional visibility"""

    field_name: str
    value: Any


class UIElementMetadata(ORMModel):
    label: str
    type: UIElementType
    required: bool
    name: str
    tooltip: Optional[str] = None
    options: Optional[dict] = None
    hidden: Optional[bool] = None
    pattern: Optional[str] = None
    initial_value: Optional[str | int | float | bool] = None
    value_prop_name: Optional[str] = None
    depends_on: Optional[FieldDependency] = None
    select_mode: Optional[str] = None  # "tags", "multiple", None
    max_count: Optional[int] = None
    disabled: Optional[bool] = None
    use_namespace_when_not_source_aligned: Optional[bool] = None
    normalize_array: Optional[bool] = None


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
    def get_ui_metadata(cls) -> List[UIElementMetadata]:
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
