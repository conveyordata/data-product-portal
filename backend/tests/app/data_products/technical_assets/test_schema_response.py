"""The result string when a plugin uses no platform service.

Built-in types take their template from PlatformService. A plugin that opts out
of platforms has no service row to read, so it declares its own template.
"""

from typing import ClassVar, Optional
from uuid import uuid4

from app.configuration.platforms.platform_services.schema import PlatformService
from app.configuration.platforms.schema_response import Platform
from app.data_products.technical_assets.schema_response import (
    GetTechnicalAssetsResponseItem,
)
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin


class PluginWithoutPlatform(TechnicalAssetPlugin):
    name: ClassVar[str] = "PluginWithoutPlatform"
    result_string_template: ClassVar[str] = "https://example.com/{repository}"

    repository: str


class PluginWithoutTemplate(TechnicalAssetPlugin):
    name: ClassVar[str] = "PluginWithoutTemplate"

    repository: str


def _service(result_string_template: str) -> PlatformService:
    return PlatformService(
        id=uuid4(),
        name="some-service",
        platform=Platform(id=uuid4(), name="some-platform"),
        result_string_template=result_string_template,
        technical_info_template="{repository}",
    )


def _item(
    configuration: TechnicalAssetPlugin, service: Optional[PlatformService]
) -> GetTechnicalAssetsResponseItem:
    return GetTechnicalAssetsResponseItem.model_construct(
        configuration=configuration,
        service=service,
        environment_configurations=[],
    )


def test_result_string__still_uses_the_platform_service_template():
    """Regression: a technical asset backed by a platform service is unchanged."""
    configuration = PluginWithoutPlatform(repository="some-repo")

    item = _item(configuration, _service("s3://bucket/{repository}"))

    assert item.result_string == "s3://bucket/some-repo"


def test_result_string__falls_back_to_the_plugin_template_without_a_service():
    configuration = PluginWithoutPlatform(repository="some-repo")

    item = _item(configuration, None)

    assert item.result_string == "https://example.com/some-repo"


def test_result_string__is_empty_when_the_plugin_declares_no_template():
    configuration = PluginWithoutTemplate(repository="some-repo")

    item = _item(configuration, None)

    assert item.result_string == ""


def test_technical_info__is_empty_without_a_platform_service():
    """There is no platform, so there are no per-environment configurations."""
    configuration = PluginWithoutPlatform(repository="some-repo")

    item = _item(configuration, None)

    assert item.technical_info == []
