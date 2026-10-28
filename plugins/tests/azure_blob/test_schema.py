import pytest

from portal_plugins.azure_blob.schema import (
    AzureBlobTechnicalAssetConfiguration,
)


def make_blob_config(
    domain: str,
    container_name: str,
    path: str,
) -> AzureBlobTechnicalAssetConfiguration:
    return AzureBlobTechnicalAssetConfiguration(
        domain=domain,
        container_name=container_name,
        path=path,
    )


class TestRenderTemplate:
    def test_resolves_storage_account_from_matching_domain(self, plugin_context):
        config = make_blob_config(
            domain="finance", container_name="data", path="output"
        )
        result = config.render_template(
            plugin_context=plugin_context,
            template="{storage_account}/{container_name}/{path}",
            storage_account_names={"finance": "financeartifacts", "hr": "hrartifacts"},
        )
        assert result == "financeartifacts/data/output"

    def test_falls_back_to_single_storage_account_for_key_default(self, plugin_context):
        config = make_blob_config(domain="", container_name="data", path="output")
        result = config.render_template(
            plugin_context=plugin_context,
            template="{storage_account}/{container_name}",
            storage_account_names={"default": "financeartifacts"},
        )
        assert result == "financeartifacts/data"

    def test_does_not_fall_back_to_single_storage_account(self, plugin_context):
        config = make_blob_config(domain="", container_name="data", path="output")
        with pytest.raises(KeyError):
            config.render_template(
                plugin_context=plugin_context,
                template="{storage_account}/{container_name}",
                storage_account_names={"finance": "financeartifacts"},
            )

    def test_does_not_fall_back_when_multiple_accounts_and_no_match(
        self, plugin_context
    ):
        config = make_blob_config(domain="", container_name="data", path="output")
        with pytest.raises(KeyError):
            config.render_template(
                plugin_context=plugin_context,
                template="{storage_account}/{container_name}",
                storage_account_names={
                    "finance": "financeartifacts",
                    "hr": "hrartifacts",
                },
            )

    def test_template_without_storage_account_placeholder(self, plugin_context):
        config = make_blob_config(
            domain="finance", container_name="data", path="output"
        )
        result = config.render_template(
            plugin_context=plugin_context,
            template="{container_name}/{path}",
            storage_account_names={"finance": "financeartifacts"},
        )
        assert result == "data/output"

    def test_empty_storage_account_names(self, plugin_context):
        config = make_blob_config(
            domain="finance", container_name="data", path="output"
        )
        with pytest.raises(KeyError):
            config.render_template(
                plugin_context=plugin_context,
                template="{storage_account}/{container_name}",
                storage_account_names={},
            )


def test_validate_configuration__stores_the_domain_name(plugin_context):
    config = make_blob_config(domain="", container_name="data", path="output")

    config.validate_configuration(plugin_context, db=None)

    assert config.domain == "finance"
