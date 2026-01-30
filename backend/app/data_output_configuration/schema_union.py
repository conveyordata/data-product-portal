"""
Dynamic Union type for data output configurations.

This module constructs the Union type dynamically from registered plugins,
allowing external plugins to be included without hardcoded imports.
"""

from typing import TYPE_CHECKING, Annotated, TypeAlias, Union, get_args

from pydantic import Field

from app.data_output_configuration.registry import PluginRegistry

# For type checking, import all known plugins statically
if TYPE_CHECKING:
    from app.data_output_configuration.databricks.schema import DatabricksDataOutput
    from app.data_output_configuration.glue.schema import GlueDataOutput
    from app.data_output_configuration.redshift.schema import RedshiftDataOutput
    from app.data_output_configuration.s3.schema import S3DataOutput
    from app.data_output_configuration.snowflake.schema import SnowflakeDataOutput

    # Static type for mypy - will be overridden at runtime
    DataOutputs: TypeAlias = Union[
        SnowflakeDataOutput,
        DatabricksDataOutput,
        GlueDataOutput,
        RedshiftDataOutput,
        S3DataOutput,
    ]
    DataOutputConfiguration: TypeAlias = Annotated[
        DataOutputs,
        Field(discriminator="configuration_type"),
    ]


def _build_data_output_union():
    """
    Build the Union type dynamically from registered plugins.

    This allows external plugins to be included without modifying this file.
    Called at module import time after plugin registry is initialized.
    """
    plugins = PluginRegistry.get_all()

    if not plugins:
        # Fallback: import internal plugins directly if registry not initialized
        # This ensures backward compatibility during testing or early imports
        from app.data_output_configuration.databricks.schema import DatabricksDataOutput
        from app.data_output_configuration.glue.schema import GlueDataOutput
        from app.data_output_configuration.redshift.schema import RedshiftDataOutput
        from app.data_output_configuration.snowflake.schema import SnowflakeDataOutput

        plugins = [
            SnowflakeDataOutput,
            DatabricksDataOutput,
            GlueDataOutput,
            RedshiftDataOutput,
        ]

        # Try to get S3 from registry or import (for backward compat)
        try:
            from app.data_output_configuration.s3.schema import S3DataOutput

            plugins.append(S3DataOutput)
        except ImportError:
            # S3 might be external plugin, will be picked up when registry initializes
            pass

    return Union[tuple(plugins)]


def _build_data_output_map():
    """
    Build the mapping of DataOutputTypes to plugin classes.

    Returns a dict mapping configuration_type enum values to plugin classes.
    """
    plugins = PluginRegistry.get_all()

    if not plugins:
        # Fallback for early imports
        from app.data_output_configuration.databricks.schema import DatabricksDataOutput
        from app.data_output_configuration.glue.schema import GlueDataOutput
        from app.data_output_configuration.redshift.schema import RedshiftDataOutput
        from app.data_output_configuration.snowflake.schema import SnowflakeDataOutput

        plugins = [
            SnowflakeDataOutput,
            DatabricksDataOutput,
            GlueDataOutput,
            RedshiftDataOutput,
        ]

        try:
            from app.data_output_configuration.s3.schema import S3DataOutput

            plugins.append(S3DataOutput)
        except ImportError:
            pass

    # Build map from configuration_type to plugin class
    plugin_map = {}
    for plugin in plugins:
        # Get the Literal type from the plugin's configuration_type field annotation
        # This is hacky but works - we get the actual enum value from the Literal type
        if (
            hasattr(plugin, "__annotations__")
            and "configuration_type" in plugin.__annotations__
        ):
            config_type_annotation = plugin.__annotations__["configuration_type"]
            # Extract the Literal value
            if hasattr(config_type_annotation, "__args__"):
                literal_values = get_args(config_type_annotation)
                if literal_values:
                    plugin_map[literal_values[0]] = plugin

    return plugin_map


# Runtime: Build dynamic types - these will be rebuilt when registry changes
if not TYPE_CHECKING:
    DataOutputs: TypeAlias = _build_data_output_union()
    DataOutputConfiguration: TypeAlias = Annotated[
        DataOutputs,
        Field(discriminator="configuration_type"),
    ]

# Always build the map (used at runtime, not for typing)
DataOutputMap = _build_data_output_map()


def rebuild_union_types():
    """
    Rebuild the union types after plugin registry changes.

    Should be called after plugin registration is complete.
    """
    global DataOutputs, DataOutputMap, DataOutputConfiguration

    DataOutputs = _build_data_output_union()
    DataOutputMap = _build_data_output_map()
    DataOutputConfiguration = Annotated[
        DataOutputs,
        Field(discriminator="configuration_type"),
    ]
