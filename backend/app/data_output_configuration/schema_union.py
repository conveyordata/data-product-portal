"""
Dynamic plugin union system using Pydantic's discriminated union pattern.

This module automatically discovers and includes all plugin configurations
at import time, ensuring the Union is always complete before any models
are defined. This works seamlessly with:
- SQLAlchemy ORM models (database layer)
- Pydantic schemas (API/validation layer)
- FastAPI OpenAPI generation
- External pip-installed plugins

The key mechanism: _build_runtime_union() triggers plugin discovery on first
import, so DataOutputConfiguration is built with all available plugins from
the start, avoiding Pydantic validator caching issues.
"""

from typing import TYPE_CHECKING, Annotated, TypeAlias, Union, get_args

from pydantic import Field

# Import base model at runtime so SQLAlchemy can resolve the relationship
from app.data_output_configuration.base_model import (
    TechnicalAssetConfiguration,  # noqa: F401
)
from app.data_output_configuration.registry import PluginRegistry

# Static imports for type checking - only internal plugins (always present)
if TYPE_CHECKING:
    from app.data_output_configuration.databricks.schema import (
        DatabricksTechnicalAssetConfiguration,
    )
    from app.data_output_configuration.glue.schema import (
        GlueTechnicalAssetConfiguration,
    )
    from app.data_output_configuration.redshift.schema import (
        RedshiftTechnicalAssetConfiguration,
    )
    from app.data_output_configuration.snowflake.schema import (
        SnowflakeTechnicalAssetConfiguration,
    )

    # Type hint for static analysis (actual Union is built dynamically at runtime)
    DataOutputs: TypeAlias = Union[
        SnowflakeTechnicalAssetConfiguration,
        DatabricksTechnicalAssetConfiguration,
        GlueTechnicalAssetConfiguration,
        RedshiftTechnicalAssetConfiguration,
    ]

    DataOutputConfiguration: TypeAlias = Annotated[
        DataOutputs,
        Field(discriminator="configuration_type"),
    ]


def _build_runtime_union() -> type:
    """
    Build Union type from all registered plugins.

    Auto-discovers plugins on first call to ensure the Union is always
    complete before any Pydantic models are defined.
    """
    plugins = PluginRegistry.get_all()

    if not plugins:
        # First import: auto-discover plugins
        from app.settings import settings

        enabled_plugins = None
        if settings.ENABLED_PLUGINS:
            enabled_plugins = [
                p.strip() for p in settings.ENABLED_PLUGINS.split(",") if p.strip()
            ]
        PluginRegistry.discover_and_register(enabled_plugins)
        plugins = PluginRegistry.get_all()

    if len(plugins) == 1:
        return plugins[0]
    return Union[tuple(plugins)]  # type: ignore


# Runtime: Build union from all plugins (discovered automatically)
if not TYPE_CHECKING:
    DataOutputs: TypeAlias = _build_runtime_union()
    DataOutputConfiguration: TypeAlias = Annotated[
        DataOutputs,  # type: ignore
        Field(discriminator="configuration_type"),
    ]


def _build_output_map() -> dict:
    """Build map of configuration_type -> plugin class for quick lookups."""
    output_map = {}
    for plugin in PluginRegistry.get_all():
        if (
            hasattr(plugin, "__annotations__")
            and "configuration_type" in plugin.__annotations__
        ):
            config_type_annotation = plugin.__annotations__["configuration_type"]
            if hasattr(config_type_annotation, "__args__"):
                literal_values = get_args(config_type_annotation)
                if literal_values:
                    enum_member = literal_values[0]
                    config_type_value = (
                        enum_member.value
                        if hasattr(enum_member, "value")
                        else enum_member
                    )
                    output_map[config_type_value] = plugin
    return output_map


# Map for quick lookups (built automatically after plugin discovery)
DataOutputMap: dict = _build_output_map()
