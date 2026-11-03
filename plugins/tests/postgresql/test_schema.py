from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.configuration.environments.model import Environment
from app.data_products.technical_assets.model import TechnicalAsset
from app.shared.model import utcnow
from app.technical_asset_configuration.base_schema import (
    EnvironmentConfigurationError,
    TechnicalAssetContext,
)
from portal_plugins.postgresql.model import PostgreSQLEnvironmentConfiguration
from portal_plugins.postgresql.schema import (
    INSTANCE_NAME_PATTERN,
    PostgreSQLEnvironmentConfigurationSchema,
    PostgreSQLTechnicalAssetConfiguration,
)


@compiles(utcnow, "sqlite")
def utcnow_sqlite(element, compiler, **kw):
    return "CURRENT_TIMESTAMP"


def metadata(acronym: str) -> dict:
    return {
        element.name: element.select
        for element in PostgreSQLEnvironmentConfigurationSchema.ui_metadata(
            Environment(acronym=acronym)
        )
    }


class TestUiMetadata:
    @pytest.mark.parametrize(
        ("acronym", "engine_version", "size", "storage_gb"),
        [
            ("dev", "17", "small", "20"),
            ("prd", "16", "medium", "50"),
            ("tst", "17", "small", "20"),
        ],
    )
    def test_ui_metadata__defaults_per_environment(
        self, acronym, engine_version, size, storage_gb
    ):
        selects = metadata(acronym)

        assert selects["engine_version"].initial_value == engine_version
        assert selects["size"].initial_value == size
        assert selects["storage_gb"].initial_value == storage_gb

    @pytest.mark.parametrize(
        ("acronym", "instance_name"),
        [
            ("dev", "{database:.16}-{schema:.36}-dev"),
            ("prd", "{database:.16}-{schema:.36}"),
            ("tst", "{database:.16}-{schema:.36}-tst"),
        ],
    )
    def test_ui_metadata__instance_name_default(self, acronym, instance_name):
        elements = {
            element.name: element
            for element in PostgreSQLEnvironmentConfigurationSchema.ui_metadata(
                Environment(acronym=acronym)
            )
        }

        assert elements["instance_name"].string.initial_value == instance_name

    def test_ui_metadata__disables_options_per_environment(self):
        def disabled(acronym, field):
            return {
                option.value
                for option in metadata(acronym)[field].options
                if option.disabled
            }

        assert disabled("prd", "engine_version") == {"18"}
        assert disabled("dev", "engine_version") == set()
        assert disabled("dev", "size") == {"large"}
        assert disabled("prd", "size") == set()

    def test_ui_metadata__defaults_are_valid_options(self):
        selects = metadata("prd")

        for field, select in selects.items():
            if select is not None:
                assert select.initial_value in {
                    option.value for option in select.options
                }
            assert field in PostgreSQLEnvironmentConfigurationSchema.model_fields


def test_defaults__instance_name_stays_valid_for_long_identifiers():
    default = PostgreSQLEnvironmentConfigurationSchema.defaults(
        Environment(acronym="dev")
    )["instance_name"]

    name = default.format(database="dpp_demo", schema="s" * 64)

    assert INSTANCE_NAME_PATTERN.fullmatch(name)


def test_environment_configuration__links_schema_to_table():
    assert (
        PostgreSQLTechnicalAssetConfiguration.environment_configuration
        is PostgreSQLEnvironmentConfigurationSchema
    )
    assert PostgreSQLEnvironmentConfigurationSchema.Meta.orm_model.__tablename__ == (
        "postgresql_environment_configurations"
    )


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    TechnicalAsset.__table__.create(engine)
    PostgreSQLEnvironmentConfiguration.__table__.create(engine)
    with Session(engine) as session:
        yield session


def store(db, name, asset_id=None):
    configuration_id = uuid4()
    if asset_id:
        db.add(
            TechnicalAsset(
                id=asset_id, owner_id=uuid4(), configuration_id=configuration_id
            )
        )
    db.add(
        PostgreSQLEnvironmentConfiguration(
            configuration_id=configuration_id,
            environment_id=uuid4(),
            engine_version="17",
            size="small",
            storage_gb=20,
            instance_name=name,
        )
    )
    db.commit()


def validate(db, plugin_context, names, asset_id=None):
    plugin_context.technical_asset = TechnicalAssetContext(
        id=asset_id,
        namespace="orders",
        technical_mapping=plugin_context.technical_asset.technical_mapping,
    )
    values = {uuid4(): {"instance_name": name} for name in names}
    plugin = PostgreSQLTechnicalAssetConfiguration.model_construct()
    try:
        plugin.validate_environment_configuration(values, plugin_context, db)
    except EnvironmentConfigurationError as error:
        return [
            (list(values).index(item.environment_id), item.message)
            for item in error.errors
        ]
    return []


class TestValidateEnvironmentConfiguration:
    def test_validate_environment_configuration__accepts_valid_names(
        self, db, plugin_context
    ):
        assert (
            validate(
                db, plugin_context, ["orders", "orders-dev", "a1-b2", "dpp_demo-dev"]
            )
            == []
        )

    @pytest.mark.parametrize("name", ["", "Orders", "1orders", "orders.dev", "a" * 64])
    def test_validate_environment_configuration__rejects_invalid_format(
        self, db, plugin_context, name
    ):
        assert validate(db, plugin_context, [name]) == [
            (
                0,
                "Use lowercase letters, digits, underscores and hyphens, starting with a letter (max 63)",
            )
        ]

    def test_validate_environment_configuration__accepts_name_of_63_characters(
        self, db, plugin_context
    ):
        assert validate(db, plugin_context, ["a" * 63]) == []

    def test_validate_environment_configuration__rejects_duplicates_within_asset(
        self, db, plugin_context
    ):
        message = "Instance name is used in another Environment of this Technical Asset"

        assert validate(db, plugin_context, ["orders", "orders-dev", "orders"]) == [
            (0, message),
            (2, message),
        ]

    def test_validate_environment_configuration__rejects_name_of_other_asset(
        self, db, plugin_context
    ):
        store(db, "orders", asset_id=uuid4())

        assert validate(db, plugin_context, ["orders", "orders-dev"]) == [
            (0, "Instance name is already used by another Technical Asset")
        ]

    def test_validate_environment_configuration__ignores_names_of_deleted_assets(
        self, db, plugin_context
    ):
        store(db, "orders")

        assert validate(db, plugin_context, ["orders"]) == []

    def test_validate_environment_configuration__ignores_own_names_on_update(
        self, db, plugin_context
    ):
        asset_id = uuid4()
        store(db, "orders", asset_id=asset_id)

        assert validate(db, plugin_context, ["orders"], asset_id=asset_id) == []

    def test_validate_environment_configuration__collects_all_errors(
        self, db, plugin_context
    ):
        store(db, "taken", asset_id=uuid4())

        errors = validate(db, plugin_context, ["taken", "Bad", "Bad"])

        assert sorted(cell for cell, _ in errors) == [0, 1, 1, 2, 2]
