"""
Spike for docs/adr/0024-dynamic-plugin-system.md, using S3 and Glue as the
example plugins. Proves, against the real test Postgres database:

1. configuration stored as one shared JSONB column, validated against the
   plugin's own declared fields at save time (not by the table schema)
2. per-environment configuration as one generic (plugin, environment) record,
   with the AWS-account duplication cost the ADR calls out
3. a plugin discovered via an explicit named list (Option 2b), carrying both
   its declarative fields and its behavior (validate/render_result/get_url/
   is_shareable)

Not wired into the real plugin system -- see app/spike_plugins/.
"""

import uuid

import pytest
from pydantic import ValidationError

from app.spike_plugins.glue import GlueEnvironmentConfig, SpikeGluePlugin
from app.spike_plugins.model import SpikeEnvironmentConfig, SpikeTechnicalAsset
from app.spike_plugins.registry import SPIKE_PLUGIN_MODULES, load_spike_plugins
from app.spike_plugins.s3 import S3EnvironmentConfig, SpikeS3Plugin
from tests.factories import DataProductFactory, EnvironmentFactory


class TestRegistry:
    def test_loads_exactly_the_explicitly_named_plugins(self):
        registry = load_spike_plugins()

        assert set(registry.keys()) == {"s3", "glue"}
        assert registry["s3"] is SpikeS3Plugin
        assert registry["glue"] is SpikeGluePlugin

    def test_nothing_is_auto_discovered(self):
        # Option 2b: the only thing that decides what loads is this list.
        # There is deliberately no scanning of installed packages / entry
        # points here -- if this list is empty, nothing loads, full stop.
        assert SPIKE_PLUGIN_MODULES == [
            "app.spike_plugins.s3:SpikeS3Plugin",
            "app.spike_plugins.glue:SpikeGluePlugin",
        ]


class TestS3ConfigValidation:
    def test_valid_config_is_accepted(self):
        plugin = SpikeS3Plugin(bucket="datalake", suffix="customer360", path="output")
        assert plugin.bucket == "datalake"

    def test_missing_required_field_is_rejected(self):
        # `path` is required -- Pydantic checks this against the plugin's own
        # declared fields, not against a database column definition.
        with pytest.raises(ValidationError):
            SpikeS3Plugin(bucket="datalake")

    def test_unknown_field_is_rejected(self):
        # extra="forbid" -- a typo or a stray field in the JSON doesn't get
        # silently ignored.
        with pytest.raises(ValidationError):
            SpikeS3Plugin(bucket="datalake", path="output", not_a_real_field="x")

    def test_render_result_looks_up_environment_config_by_bucket_name(self):
        plugin = SpikeS3Plugin(bucket="datalake", suffix="customer360", path="output")
        env_config = {
            "account_id": "111111111111",
            "region": "eu-west-1",
            "bucket_arns": {"datalake": "arn:aws:s3:::datalake-prod"},
        }
        assert (
            plugin.render_result(env_config)
            == "arn:aws:s3:::datalake-prod/customer360/output/*"
        )

    def test_render_result_fails_loudly_for_unconfigured_bucket(self):
        plugin = SpikeS3Plugin(bucket="unknown-bucket", path="output")
        env_config = {
            "account_id": "111111111111",
            "region": "eu-west-1",
            "bucket_arns": {"datalake": "arn:aws:s3:::datalake-prod"},
        }
        with pytest.raises(ValueError, match="No ARN configured"):
            plugin.render_result(env_config)


class TestGlueConfigValidation:
    def test_database_must_start_with_namespace(self):
        plugin = SpikeGluePlugin(database="marketing_customers", table="customers")
        plugin.validate_configuration(namespace="marketing")  # does not raise

        with pytest.raises(ValueError, match="must start with namespace"):
            plugin.validate_configuration(namespace="finance")

    def test_render_result_strips_trailing_underscores(self):
        plugin = SpikeGluePlugin(database="marketing_", table="customers_")
        assert plugin.render_result({}) == "marketing.customers"


class TestIsShareableHook:
    def test_default_is_shareable(self):
        assert SpikeS3Plugin(bucket="b", path="p").is_shareable() is True
        assert SpikeGluePlugin(database="d", table="t").is_shareable() is True


class TestStoredConfigRoundTrip:
    """Point 1: one shared JSONB column instead of a table per plugin type."""

    def test_s3_and_glue_share_one_table_and_round_trip_through_postgres(self, session):
        data_product = DataProductFactory()

        s3_row = SpikeTechnicalAsset(
            id=uuid.uuid4(),
            data_product_id=data_product.id,
            plugin_key="s3",
            config={"bucket": "datalake", "suffix": "customer360", "path": "output"},
        )
        glue_row = SpikeTechnicalAsset(
            id=uuid.uuid4(),
            data_product_id=data_product.id,
            plugin_key="glue",
            config={"database": "marketing_customers", "table": "customers"},
        )
        session.add_all([s3_row, glue_row])
        session.flush()

        # Same table, both rows -- prove it by re-reading from the DB and
        # reconstructing the right plugin class from the stored JSON, purely
        # by field name, the way the real render_template already does today.
        registry = load_spike_plugins()

        stored_s3 = session.get(SpikeTechnicalAsset, s3_row.id)
        s3_plugin = registry[stored_s3.plugin_key](**stored_s3.config)
        assert (
            s3_plugin.render_result(
                {
                    "account_id": "1",
                    "region": "eu-west-1",
                    "bucket_arns": {"datalake": "arn:x"},
                }
            )
            == "arn:x/customer360/output/*"
        )

        stored_glue = session.get(SpikeTechnicalAsset, glue_row.id)
        glue_plugin = registry[stored_glue.plugin_key](**stored_glue.config)
        glue_plugin.validate_configuration(namespace="marketing")
        assert glue_plugin.render_result({}) == "marketing_customers.customers"

    def test_bad_stored_json_is_still_caught_at_read_time(self, session):
        # Simulates a corrupt/hand-edited row: storage doesn't enforce shape,
        # but reconstructing the plugin from it still validates against the
        # plugin's declared fields.
        data_product = DataProductFactory()
        row = SpikeTechnicalAsset(
            id=uuid.uuid4(),
            data_product_id=data_product.id,
            plugin_key="s3",
            config={"bucket": "datalake"},  # missing required `path`
        )
        session.add(row)
        session.flush()

        stored = session.get(SpikeTechnicalAsset, row.id)
        with pytest.raises(ValidationError):
            SpikeS3Plugin(**stored.config)


class TestEnvironmentConfig:
    """Point 2: one generic (plugin, environment) record, and the
    account-id duplication cost this decision accepts."""

    def test_s3_and_glue_each_own_their_environment_shape(self, session):
        dev = EnvironmentFactory()

        s3_env = SpikeEnvironmentConfig(
            id=uuid.uuid4(),
            plugin_key="s3",
            environment_id=dev.id,
            config={
                "account_id": "222222222222",
                "region": "eu-west-1",
                "bucket_arns": {"datalake": "arn:aws:s3:::datalake-dev"},
            },
        )
        glue_env = SpikeEnvironmentConfig(
            id=uuid.uuid4(),
            plugin_key="glue",
            environment_id=dev.id,
            # Same AWS account as S3 above -- but there is no shared place to
            # read it from, so it's re-typed here, in Glue's own record.
            config={"account_id": "222222222222", "region": "eu-west-1"},
        )
        session.add_all([s3_env, glue_env])
        session.flush()

        stored_s3_env = session.get(SpikeEnvironmentConfig, s3_env.id)
        stored_glue_env = session.get(SpikeEnvironmentConfig, glue_env.id)

        # The duplication, measured: the same account_id genuinely lives in
        # two separate rows, not referenced from one shared place.
        assert stored_s3_env.config["account_id"] == "222222222222"
        assert stored_glue_env.config["account_id"] == "222222222222"
        assert stored_s3_env.id != stored_glue_env.id  # two real, separate rows

        # And they're validated independently, against each plugin's own
        # environment_fields shape:
        S3EnvironmentConfig.model_validate(stored_s3_env.config)
        GlueEnvironmentConfig.model_validate(stored_glue_env.config)
        with pytest.raises(ValidationError):
            # Glue's shape has no bucket_arns -- it's a different shape.
            GlueEnvironmentConfig.model_validate(stored_s3_env.config)

    def test_get_url_uses_stored_environment_config(self, session):
        dev = EnvironmentFactory()
        env_row = SpikeEnvironmentConfig(
            id=uuid.uuid4(),
            plugin_key="glue",
            environment_id=dev.id,
            config={"account_id": "333333333333", "region": "us-east-1"},
        )
        session.add(env_row)
        session.flush()

        stored = session.get(SpikeEnvironmentConfig, env_row.id)
        plugin = SpikeGluePlugin(database="marketing", table="customers")
        url = plugin.get_url(stored.config)
        assert "333333333333" in url
        assert "us-east-1" in url
