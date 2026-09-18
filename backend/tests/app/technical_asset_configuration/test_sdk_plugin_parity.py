import pytest
import sdk.plugins as sdk_plugins

from app.plugins.registry import plugin_registry

PLUGIN_PAIRS = [
    (getattr(sdk_plugins, plugin.__name__), plugin)
    for plugin in plugin_registry.discovered()
    if hasattr(plugin, "Meta")
]


def test_plugin_pairs__covers_every_plugin_with_a_configuration():
    assert PLUGIN_PAIRS


@pytest.mark.parametrize(("sdk_model", "plugin"), PLUGIN_PAIRS)
def test_sdk_plugin_models__declare_the_same_fields(sdk_model, plugin):
    assert set(sdk_model.model_fields) == set(plugin.model_fields)


@pytest.mark.parametrize(("sdk_model", "plugin"), PLUGIN_PAIRS)
def test_sdk_plugin_models__use_the_same_name(sdk_model, plugin):
    assert sdk_model.name == plugin.name


@pytest.mark.parametrize(("sdk_model", "plugin"), PLUGIN_PAIRS)
def test_sdk_plugin_models__declare_the_same_defaults(sdk_model, plugin):
    sdk_defaults = {n: f.default for n, f in sdk_model.model_fields.items()}
    plugin_defaults = {n: f.default for n, f in plugin.model_fields.items()}

    assert sdk_defaults == plugin_defaults
