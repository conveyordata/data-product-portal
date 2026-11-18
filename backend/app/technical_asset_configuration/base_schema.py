from abc import ABC
from base64 import b64encode
from dataclasses import dataclass
from enum import Enum
from functools import cache
from importlib import resources
from typing import TYPE_CHECKING, Any, ClassVar, Optional, get_args
from uuid import UUID

from pydantic import ConfigDict, Field, computed_field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.configuration.domains.schema import Domain
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
from app.data_products.schema import DataProduct
from app.data_products.technical_assets.enums import TechnicalMapping
from app.shared.schema import ORMModel
from app.technical_asset_configuration.enums import UIElementType
from app.users.schema import User

if TYPE_CHECKING:
    from app.configuration.environments.model import Environment as EnvironmentModel
    from app.data_products.model import DataProduct as DataProductModel


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
    value: str | bool | int
    disabled: Optional[bool] = None


class UIElementCheckbox(ORMModel):
    initial_value: Optional[bool] = None


class UIElementRadio(ORMModel):
    max_count: Optional[int] = 1
    initial_value: Optional[str] = None
    options: Optional[list[SelectOption]] = None  # Additional options for radio fields


class UIElementSelect(ORMModel):
    max_count: Optional[int] = 1
    initial_value: Optional[str] = None
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


class EnvironmentFieldError(ORMModel):
    environment_id: UUID
    field: Optional[str] = None
    message: str


class EnvironmentConfigurationError(Exception):
    def __init__(self, errors: list[EnvironmentFieldError]):
        super().__init__("Invalid environment configuration")
        self.errors = errors


@dataclass(frozen=True)
class EnvironmentField:
    label: str
    type: UIElementType
    default: Any
    options: Optional[list[SelectOption]]
    default_per_environment: dict[str, Any]
    disabled_per_environment: dict[str, set[Any]]
    tooltip: Optional[str]


def env_field(
    label: str,
    type: UIElementType,
    default: Any,
    options: Optional[list[SelectOption]] = None,
    default_per_environment: Optional[dict[str, Any]] = None,
    disabled_per_environment: Optional[dict[str, set[Any]]] = None,
    tooltip: Optional[str] = None,
) -> Any:
    info = Field()
    info.metadata.append(
        EnvironmentField(
            label=label,
            type=type,
            default=default,
            options=options,
            default_per_environment=default_per_environment or {},
            disabled_per_environment=disabled_per_environment or {},
            tooltip=tooltip,
        )
    )
    return info


def _raw(value: Any) -> Any:
    return value.value if isinstance(value, Enum) else value


class EnvironmentSettings(ORMModel):
    model_config = ConfigDict(extra="forbid")

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)
        for name, (annotation, declaration) in cls.environment_fields().items():
            problem = cls._declaration_problem(annotation, declaration)
            if problem:
                raise TypeError(f"{cls.__name__}.{name}: {problem}")

    @classmethod
    def environment_fields(cls) -> dict[str, tuple[Any, EnvironmentField]]:
        fields = {}
        for name, info in cls.model_fields.items():
            declaration = next(
                (item for item in info.metadata if isinstance(item, EnvironmentField)),
                None,
            )
            if declaration is None:
                raise TypeError(
                    f"{cls.__name__}.{name} must be declared with env_field"
                )
            fields[name] = (info.annotation, declaration)
        return fields

    @classmethod
    def defaults(cls, environment: "EnvironmentModel") -> dict[str, Any]:
        defaults = {}
        for name, (_, declaration) in cls.environment_fields().items():
            value = _raw(
                declaration.default_per_environment.get(
                    environment.acronym, declaration.default
                )
            )
            if isinstance(value, str):
                value = value.replace("{environment}", environment.acronym)
            defaults[name] = value
        return defaults

    @classmethod
    def allowed_options(cls, environment: "EnvironmentModel") -> dict[str, set[Any]]:
        return {
            name: {
                _raw(option.value)
                for option in declaration.options
                if option.value
                not in declaration.disabled_per_environment.get(
                    environment.acronym, set()
                )
            }
            for name, (_, declaration) in cls.environment_fields().items()
            if declaration.options is not None
        }

    @classmethod
    def ui_metadata(cls, environment: "EnvironmentModel") -> list[UIElementMetadata]:
        defaults = cls.defaults(environment)
        allowed = cls.allowed_options(environment)
        elements = []
        for name, (_, declaration) in cls.environment_fields().items():
            control: dict[str, Any] = {}
            if declaration.options is not None:
                options = [
                    SelectOption(
                        label=option.label,
                        value=str(_raw(option.value)),
                        disabled=_raw(option.value) not in allowed[name],
                    )
                    for option in declaration.options
                ]
                if declaration.type == UIElementType.Select:
                    control["select"] = UIElementSelect(
                        initial_value=str(defaults[name]), options=options
                    )
                else:
                    control["radio"] = UIElementRadio(
                        initial_value=str(defaults[name]), options=options
                    )
            elif declaration.type == UIElementType.Checkbox:
                control["checkbox"] = UIElementCheckbox(initial_value=defaults[name])
            else:
                control["string"] = UIElementString(initial_value=str(defaults[name]))
            elements.append(
                UIElementMetadata(
                    name=name,
                    label=declaration.label,
                    tooltip=declaration.tooltip,
                    required=True,
                    type=declaration.type,
                    **control,
                )
            )
        return elements

    @staticmethod
    def _declaration_problem(
        annotation: Any, declaration: EnvironmentField
    ) -> Optional[str]:
        if type(None) in get_args(annotation):
            return "per-Environment fields are required, Optional isn't supported yet"
        is_enum = isinstance(annotation, type) and issubclass(annotation, Enum)
        if declaration.type in (UIElementType.Select, UIElementType.Radio):
            if not is_enum or declaration.options is None:
                return f"{declaration.type.value} needs an Enum type and options"
            values = [_raw(option.value) for option in declaration.options]
            if len(values) != len(annotation) or set(values) != {
                member.value for member in annotation
            }:
                return "options must list every member of the Enum exactly once"
            return None
        if declaration.options is not None:
            return f"{declaration.type.value} takes no options"
        if declaration.type == UIElementType.Checkbox and annotation is not bool:
            return "checkbox needs a bool type"
        if declaration.type == UIElementType.String and is_enum:
            return "an Enum needs a select or radio"
        return None


class TechnicalAssetPlugin(ORMModel, ABC):
    version: ClassVar[str] = "1.0"
    mcp_instructions: ClassVar[str] = ""
    environment_configuration: ClassVar[Optional[type[EnvironmentSettings]]] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name(self) -> str:
        raise NotImplementedError

    _platform_metadata: ClassVar[Optional[PlatformMetadata]] = None

    def render_template(
        self, template: str, *, plugin_context: PluginContext, **context: Any
    ) -> str:
        return template.format(
            **{**dict(plugin_context), **self.model_dump(), **context}
        )

    def get_configuration(self, configs: list[ConfigType]) -> Optional[ConfigType]:
        raise NotImplementedError

    def validate_configuration(self, context: PluginContext, db: Session) -> None:
        """Raise when the configuration isn't acceptable, on create with the default technical mapping."""

    def validate_environment_configuration(
        self,
        values: dict[UUID, dict[str, Any]],
        context: PluginContext,
        db: Session,
    ) -> None:
        """Raise EnvironmentConfigurationError when the values of all Environments, keyed by environment id, aren't acceptable."""

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
                detailed_name=class_name,
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
