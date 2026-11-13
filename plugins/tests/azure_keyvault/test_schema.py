from unittest.mock import Mock
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from portal_plugins.azure_keyvault.schema import (
    AzureKeyVaultTechnicalAssetConfiguration,
)

METADATA = AzureKeyVaultTechnicalAssetConfiguration.get_platform_metadata()


def context_with(plugin_context, **values):
    return plugin_context.model_copy(
        update={
            "technical_asset": plugin_context.technical_asset.model_copy(update=values)
        }
    )


@pytest.fixture
def db():
    session = Mock(spec=Session)
    session.scalar.return_value = False
    return session


def test_render_template__previews_name_without_changing_configuration(plugin_context):
    config = AzureKeyVaultTechnicalAssetConfiguration()

    assert (
        config.render_template(
            METADATA.result_string_template, plugin_context=plugin_context
        )
        == "kv-adp-order-secrets"
    )
    assert (
        config.render_template(
            METADATA.result_string_template,
            plugin_context=context_with(plugin_context, name="new-secrets"),
        )
        == "kv-adp-new-secrets"
    )
    assert config.vault_name == ""


def test_render_template__uses_stored_name_after_display_name_changes(plugin_context):
    config = AzureKeyVaultTechnicalAssetConfiguration(vault_name="kv-adp-original")
    context = context_with(plugin_context, id=uuid4(), name="Renamed secrets!")

    assert (
        config.render_template(METADATA.result_string_template, plugin_context=context)
        == "kv-adp-original"
    )
    assert (
        config.render_template(
            METADATA.technical_info_template,
            plugin_context=context,
            environment="prd",
        )
        == "https://kv-adp-original-prd.vault.azure.net/"
    )


def test_render_template__rejects_missing_stored_name(plugin_context):
    config = AzureKeyVaultTechnicalAssetConfiguration()

    with pytest.raises(ValueError, match="missing its stored vault name"):
        config.render_template(
            METADATA.result_string_template,
            plugin_context=context_with(plugin_context, id=uuid4()),
        )


def test_validate_configuration__stores_name_and_leaves_namespace_unchanged(
    plugin_context, db
):
    context = context_with(
        plugin_context, name="copilot-usage", namespace="namespace-longer-than-thirteen"
    )
    config = AzureKeyVaultTechnicalAssetConfiguration(vault_name="client-override")

    config.validate_configuration(context, db)

    assert config.vault_name == "kv-adp-copilot-usage"
    assert context.technical_asset.namespace == "namespace-longer-than-thirteen"


@pytest.mark.parametrize(
    ("name", "message"),
    [
        ("", "include a name"),
        ("a" * 14, "maximum 20 characters"),
        ("MyVault", "lowercase letters"),
        ("my_vault", "lowercase letters"),
        ("my.vault", "lowercase letters"),
        ("my vault", "lowercase letters"),
        ("my--vault", "consecutive hyphens"),
        ("-vault", "consecutive hyphens"),
    ],
)
def test_validate_configuration__rejects_invalid_names(
    plugin_context, db, name, message
):
    config = AzureKeyVaultTechnicalAssetConfiguration()

    with pytest.raises(ValueError, match=message):
        config.validate_configuration(context_with(plugin_context, name=name), db)

    db.scalar.assert_not_called()
    assert config.vault_name == ""


def test_validate_configuration__accepts_thirteen_character_name(plugin_context, db):
    config = AzureKeyVaultTechnicalAssetConfiguration()

    config.validate_configuration(context_with(plugin_context, name="a" * 13), db)

    assert config.vault_name == f"kv-adp-{'a' * 13}"


def test_validate_configuration__rejects_an_existing_key_vault(plugin_context, db):
    db.scalar.return_value = True
    config = AzureKeyVaultTechnicalAssetConfiguration()

    with pytest.raises(ValueError, match="already exists"):
        config.validate_configuration(plugin_context, db)

    assert config.vault_name == ""
