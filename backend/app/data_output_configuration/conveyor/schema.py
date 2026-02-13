from typing import ClassVar

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)


class ConveyorPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "ConveyorPlatform"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="Conveyor",
        icon_name="conveyor-logo.svg",
        platform_key="conveyor",
        parent_platform=None,
        has_environments=False,
        detailed_name="Conveyor",
        show_in_form=False,
    )

    @classmethod
    def only_tile(cls) -> bool:
        """Conveyor is currently only shown as a tile in the UI, as it doesn't have technical assets or detailed configuration options."""
        return True
