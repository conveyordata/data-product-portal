from typing import ClassVar

from app.data_output_configuration.base_schema import (
    AssetProviderPlugin,
    PlatformMetadata,
)


class CoderPlugin(AssetProviderPlugin):
    name: ClassVar[str] = "CoderPlatform"
    version: ClassVar[str] = "1.0"

    _platform_metadata = PlatformMetadata(
        display_name="VS Code",
        icon_name="coder-logo.svg",
        platform_key="coder",
        parent_platform=None,
        has_environments=False,
        detailed_name="VS Code - Coder",
    )
