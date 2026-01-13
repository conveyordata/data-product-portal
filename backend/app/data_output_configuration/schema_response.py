from typing import Optional, Sequence

from app.data_output_configuration.base_schema import UIElementMetadata
from app.shared.schema import ORMModel


class PlatformTile(ORMModel):
    """Represents a platform tile in the UI"""

    label: str
    value: str  # platform identifier
    icon_name: str
    has_menu: bool = True
    has_config: bool = True
    children: list["PlatformTile"] = []


class UIElementMetadataResponse(ORMModel):
    ui_metadata: Sequence[UIElementMetadata]
    plugin: str
    result_label: str = "Resulting path"
    result_tooltip: str = "The path you can access through this technical asset"
    platform: str  # e.g., "s3", "redshift", "snowflake"
    display_name: str  # Display name for the platform tile
    icon_name: str  # Icon filename (e.g., "s3-logo.svg")
    parent_platform: Optional[str] = None  # e.g., "aws" for s3, redshift, glue
    platform_tile: Optional[PlatformTile] = None  # Complete tile structure


class PluginResponse(ORMModel):
    """Response model for listing available plugins"""

    plugins: Sequence[UIElementMetadataResponse]


class PlatformTileResponse(ORMModel):
    """Response model for platform tiles"""

    platform_tiles: Sequence[PlatformTile]
