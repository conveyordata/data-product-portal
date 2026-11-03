from base64 import b64decode
from enum import Enum
from typing import ClassVar, Optional

import pytest
from pydantic import create_model

from app.configuration.environments.model import Environment
from app.technical_asset_configuration.base_schema import (
    EnvironmentSettings,
    PlatformMetadata,
    SelectOption,
    TechnicalAssetPlugin,
    env_field,
)
from app.technical_asset_configuration.enums import UIElementType


class PluginWithBundledIcon(TechnicalAssetPlugin):
    name: ClassVar[str] = "PluginWithBundledIcon"

    _platform_metadata = PlatformMetadata(
        display_name="Bundled icon",
        icon_name="icon.svg",
        icon_package="tests.fixtures.example_plugin",
        platform_key="bundled-icon-test",
        detailed_name="Bundled icon",
    )


def test_get_icon_data_uri__encodes_the_icon_bundled_in_the_package():
    data_uri = PluginWithBundledIcon.get_icon_data_uri()

    assert data_uri.startswith("data:image/svg+xml;base64,")
    decoded = b64decode(data_uri.removeprefix("data:image/svg+xml;base64,"))
    assert decoded.startswith(b"<svg")


class PluginWithBrokenIcon(TechnicalAssetPlugin):
    name: ClassVar[str] = "PluginWithBrokenIcon"

    _platform_metadata = PlatformMetadata(
        display_name="Broken icon",
        icon_name="does-not-exist.svg",
        icon_package="tests.fixtures.example_plugin",
        platform_key="broken-icon-test",
        detailed_name="Broken icon",
    )


def test_get_icon_data_uri__returns_none_when_the_icon_cannot_be_read():
    assert PluginWithBrokenIcon.get_icon_data_uri() is None


def test_get_icon_data_uri__reads_the_icon_once_per_plugin():
    PluginWithBundledIcon.get_icon_data_uri.cache_clear()

    first = PluginWithBundledIcon.get_icon_data_uri()
    second = PluginWithBundledIcon.get_icon_data_uri()

    assert first == second
    assert PluginWithBundledIcon.get_icon_data_uri.cache_info().hits == 1


class Colour(str, Enum):
    red = "red"
    blue = "blue"


COLOUR_OPTIONS = [
    SelectOption(label="Red", value=Colour.red),
    SelectOption(label="Blue", value=Colour.blue),
]


def declare(annotation, **declaration):
    return create_model(
        "Declared",
        __base__=EnvironmentSettings,
        value=(annotation, env_field(label="Value", **declaration)),
    )


class TestEnvironmentSettings:
    @pytest.mark.parametrize(
        ("annotation", "declaration"),
        [
            (str, {"type": UIElementType.Select, "options": COLOUR_OPTIONS}),
            (Colour, {"type": UIElementType.Select}),
            (Colour, {"type": UIElementType.Select, "options": COLOUR_OPTIONS[:1]}),
            (
                Colour,
                {"type": UIElementType.Radio, "options": COLOUR_OPTIONS * 2},
            ),
            (Colour, {"type": UIElementType.String}),
            (str, {"type": UIElementType.String, "options": COLOUR_OPTIONS}),
            (str, {"type": UIElementType.Checkbox}),
            (Optional[str], {"type": UIElementType.String}),
            (
                Optional[Colour],
                {"type": UIElementType.Select, "options": COLOUR_OPTIONS},
            ),
        ],
    )
    def test_init_subclass__rejects_mismatched_declaration(
        self, annotation, declaration
    ):
        with pytest.raises(TypeError, match="Declared.value"):
            declare(annotation, default=None, **declaration)

    def test_ui_metadata__uses_declared_control_and_labels(self):
        settings = declare(
            Colour,
            type=UIElementType.Radio,
            options=COLOUR_OPTIONS,
            default=Colour.red,
            disabled_per_environment={"dev": {Colour.blue}},
        )

        [element] = settings.ui_metadata(Environment(acronym="dev"))

        assert element.type == UIElementType.Radio
        assert element.radio.initial_value == "red"
        assert [
            (option.label, option.value, option.disabled)
            for option in element.radio.options
        ] == [("Red", "red", False), ("Blue", "blue", True)]
