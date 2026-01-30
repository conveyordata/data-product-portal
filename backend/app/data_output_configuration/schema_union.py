"""
Dynamic plugin union system using Pydantic's discriminated union pattern.

This module provides a proper, Pythonic solution for handling plugin configurations
that can be registered at runtime. It works seamlessly with:
- SQLAlchemy ORM models (database layer)
- Pydantic schemas (API/validation layer)
- FastAPI OpenAPI generation
- External pip-installed plugins

Architecture:
1. Plugins register their Pydantic schema classes at startup
2. We build a Union of all registered schemas
3. Pydantic's from_attributes=True handles ORM → schema conversion
4. The discriminator field ("configuration_type") routes to the correct schema
"""

from typing import TYPE_CHECKING, Annotated, TypeAlias, Union, get_args

from pydantic import Field

from app.core.logging import logger

# Import base model at runtime so SQLAlchemy can resolve the relationship
from app.data_output_configuration.base_model import (
    TechnicalAssetConfiguration,  # noqa: F401
)
from app.data_output_configuration.registry import PluginRegistry

# Static imports for type checking
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

    try:
        from s3_plugin.schema import S3TechnicalAssetConfiguration
    except ImportError:
        S3TechnicalAssetConfiguration = None  # type: ignore

    # For type checkers, provide the union with known plugins
    if S3TechnicalAssetConfiguration is not None:
        DataOutputs: TypeAlias = Union[
            SnowflakeTechnicalAssetConfiguration,
            DatabricksTechnicalAssetConfiguration,
            GlueTechnicalAssetConfiguration,
            RedshiftTechnicalAssetConfiguration,
            S3TechnicalAssetConfiguration,
        ]
    else:
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
    Build the actual Union type from all registered plugins at runtime.

    This is called after plugin discovery to create a proper Pydantic Union
    that includes all plugins (internal + external).

    If plugins haven't been discovered yet, this will trigger discovery
    to ensure the Union always includes all available plugins.
    """
    plugins = PluginRegistry.get_all()

    if not plugins:
        # First time: discover plugins before building Union
        # This ensures the Union is always complete, even on first import
        from app.settings import settings

        enabled_plugins = None
        if settings.ENABLED_PLUGINS:
            enabled_plugins = [
                p.strip() for p in settings.ENABLED_PLUGINS.split(",") if p.strip()
            ]
        PluginRegistry.discover_and_register(enabled_plugins)
        plugins = PluginRegistry.get_all()

        if not plugins:
            # Still no plugins - fall back to internal ones
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

            plugins = [
                SnowflakeTechnicalAssetConfiguration,
                DatabricksTechnicalAssetConfiguration,
                GlueTechnicalAssetConfiguration,
                RedshiftTechnicalAssetConfiguration,
            ]

    # Build Union from plugin schema classes
    if len(plugins) == 1:
        return plugins[0]
    else:
        return Union[tuple(plugins)]  # type: ignore


# Runtime: Build actual union from registered plugins
if not TYPE_CHECKING:
    # Initialize with internal plugins (will be rebuilt after plugin discovery)
    DataOutputs: TypeAlias = _build_runtime_union()
    DataOutputConfiguration: TypeAlias = Annotated[
        DataOutputs,  # type: ignore
        Field(discriminator="configuration_type"),
    ]


# Map for quick lookups
DataOutputMap: dict = {}


def rebuild_union_types():
    """
    Rebuild the union type after plugins are registered.

    CRITICAL: This must be called:
    1. AFTER PluginRegistry.discover_and_register()
    2. BEFORE any FastAPI routes are processed
    3. BEFORE any Pydantic models using DataOutputConfiguration are instantiated

    This ensures the OpenAPI schema includes all registered plugins.
    """
    global DataOutputs, DataOutputConfiguration, DataOutputMap

    # Get all registered plugins
    plugins = PluginRegistry.get_all()

    # Build the map for quick lookups
    DataOutputMap = {}
    for plugin in plugins:
        if (
            hasattr(plugin, "__annotations__")
            and "configuration_type" in plugin.__annotations__
        ):
            config_type_annotation = plugin.__annotations__["configuration_type"]
            if hasattr(config_type_annotation, "__args__"):
                literal_values = get_args(config_type_annotation)
                if literal_values:
                    # Extract the enum value (string) from the enum member
                    enum_member = literal_values[0]
                    config_type_value = (
                        enum_member.value
                        if hasattr(enum_member, "value")
                        else enum_member
                    )
                    DataOutputMap[config_type_value] = plugin

    # Rebuild the Union type with all registered plugins
    DataOutputs = _build_runtime_union()
    DataOutputConfiguration = Annotated[
        DataOutputs,  # type: ignore
        Field(discriminator="configuration_type"),
    ]

    # Debug: Log what's in the Union
    union_types = (
        get_args(DataOutputs) if hasattr(DataOutputs, "__args__") else (DataOutputs,)
    )
    logger.debug(
        f"Rebuilt Union with {len(union_types)} types: {[t.__name__ for t in union_types]}"
    )

    # Update module global so imports get the new version
    import sys

    current_module = sys.modules[__name__]
    setattr(current_module, "DataOutputs", DataOutputs)
    setattr(current_module, "DataOutputConfiguration", DataOutputConfiguration)
    setattr(current_module, "DataOutputMap", DataOutputMap)

    logger.debug(
        f"Updated module globals - DataOutputConfiguration is now: {DataOutputConfiguration}"
    )

    # Force rebuild of models that use DataOutputConfiguration
    # Import here to avoid circular dependency
    try:
        from app.data_products.schema_response import (
            DataOutputLinks,
            DataProductGet,
        )
        from app.data_products.technical_assets.schema_request import (
            CreateTechnicalAssetRequest,
        )
        from app.data_products.technical_assets.schema_response import (
            BaseDataOutputGet,
            BaseTechnicalAssetGet,
        )

        # Rebuild these models to pick up the new union
        # Start with the base models
        BaseTechnicalAssetGet.model_rebuild(force=True)
        logger.debug(
            f"BaseTechnicalAssetGet.configuration type after rebuild: {BaseTechnicalAssetGet.model_fields['configuration'].annotation}"
        )

        BaseDataOutputGet.model_rebuild(force=True)
        CreateTechnicalAssetRequest.model_rebuild(force=True)

        # Then rebuild models that depend on them
        DataOutputLinks.model_rebuild(force=True)
        DataProductGet.model_rebuild(force=True)
        logger.debug(
            f"DataProductGet.data_outputs type after rebuild: {DataProductGet.model_fields['data_outputs'].annotation}"
        )

        logger.info("Rebuilt Pydantic models to use updated union")
    except Exception as e:
        logger.warning(
            f"Could not rebuild models: {e}. Models may use old union definition."
        )

    logger.info(
        f"Rebuilt union types with {len(DataOutputMap)} plugin configurations: {list(DataOutputMap.keys())}"
    )
