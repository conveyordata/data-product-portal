import pytest
from pydantic import ValidationError

from portal_plugins.parameter_store.schema import (
    ParameterStoreTechnicalAssetConfiguration,
)

RESULT_TEMPLATE = "/{prefix}/{parameter_name}"
TECHNICAL_INFO_TEMPLATE = "/{environment}/{prefix}/{parameter_name}"


def test_render_template__joins_prefix_and_parameter_name():
    config = ParameterStoreTechnicalAssetConfiguration(
        prefix="customer360", parameter_name="api-key"
    )

    assert config.render_template(RESULT_TEMPLATE) == "/customer360/api-key"


def test_render_template__skips_an_empty_prefix():
    config = ParameterStoreTechnicalAssetConfiguration(
        prefix="", parameter_name="api-key"
    )

    assert config.render_template(RESULT_TEMPLATE) == "/api-key"


def test_render_template__starts_with_the_environment():
    config = ParameterStoreTechnicalAssetConfiguration(
        prefix="customer_360", parameter_name="db/password"
    )

    assert (
        config.render_template(TECHNICAL_INFO_TEMPLATE, environment="dev")
        == "/dev/customer_360/db/password"
    )


@pytest.mark.parametrize(
    "parameter_name",
    ["api-key", "api_key", "api.key", "API-Key_1.0", "db/password", "/db/password/"],
)
def test_validate_parameter_name__accepts_valid_names(parameter_name):
    ParameterStoreTechnicalAssetConfiguration(
        prefix="customer_360", parameter_name=parameter_name
    )


@pytest.mark.parametrize("parameter_name", ["api key", "api+key", "api@key", "", "/"])
def test_validate_parameter_name__rejects_invalid_names(parameter_name):
    with pytest.raises(ValidationError):
        ParameterStoreTechnicalAssetConfiguration(
            prefix="customer_360", parameter_name=parameter_name
        )


def test_validate_parameter_name__rejects_a_namespace_aws_does_not_allow():
    with pytest.raises(ValidationError):
        ParameterStoreTechnicalAssetConfiguration(
            prefix="team+one", parameter_name="api-key"
        )


def test_validate_parameter_name__rejects_more_than_fifteen_levels():
    with pytest.raises(ValidationError):
        ParameterStoreTechnicalAssetConfiguration(
            prefix="customer_360", parameter_name="/".join(["level"] * 14)
        )


def test_validate_parameter_name__accepts_fifteen_levels():
    ParameterStoreTechnicalAssetConfiguration(
        prefix="customer_360", parameter_name="/".join(["level"] * 13)
    )


def test_validate_parameter_name__rejects_a_name_that_is_too_long():
    with pytest.raises(ValidationError):
        ParameterStoreTechnicalAssetConfiguration(
            prefix="customer_360", parameter_name="a" * 1000
        )
