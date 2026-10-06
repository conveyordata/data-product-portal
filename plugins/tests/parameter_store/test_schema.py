from portal_plugins.parameter_store.schema import (
    ParameterStoreTechnicalAssetConfiguration,
)

TEMPLATE = "/{prefix}/{parameter_name}"


def test_render_template__joins_prefix_and_parameter_name():
    config = ParameterStoreTechnicalAssetConfiguration(
        prefix="customer360", parameter_name="api-key"
    )

    assert config.render_template(TEMPLATE) == "/customer360/api-key"


def test_render_template__skips_an_empty_prefix():
    config = ParameterStoreTechnicalAssetConfiguration(
        prefix="", parameter_name="api-key"
    )

    assert config.render_template(TEMPLATE) == "/api-key"
