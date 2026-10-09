import os
import subprocess
import sys
from contextlib import suppress
from typing import ClassVar
from uuid import uuid4

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine, inspect
from sqlalchemy.exc import ProgrammingError
from sqlalchemy_utils.functions import (
    create_database,
    database_exists,
    drop_database,
)

from app.plugins.migrations import (
    _CORE_VERSIONS_DIR,
    RETIRED_PLUGIN_REVISIONS,
    VERSION_TABLE,
    _config,
    _configuration_table,
    _core_head,
    _owned_versions_dir,
    _version_locations,
    _version_table,
    check_latest_migration_core,
    migrate_all,
    owns_a_table,
)
from app.plugins.registry import plugin_registry
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin
from tests import engine
from tests.factories import TechnicalAssetFactory
from tests.fixtures.broken_plugin import BrokenPlugin
from tests.fixtures.example_plugin import ExamplePlugin
from tests.fixtures.other_plugin import OtherPlugin


def installed() -> list:
    """The plugins the portal itself would reconcile, e.g. S3.

    migrate_all is always called with every installed plugin, because the
    version table is shared and Alembic resolves every row in it. Passing a
    subset is what an uninstalled plugin looks like, which is its own test.
    """
    return [p for p in plugin_registry.discovered() if owns_a_table(p)]


def migrate(*plugins) -> None:
    migrate_all([*installed(), *plugins], engine)


@pytest.fixture(autouse=True)
def _clean_fixture_plugins():
    yield
    fixtures = [ExamplePlugin, OtherPlugin]
    url = engine.url.render_as_string(hide_password=False)
    # One config covering core and every fixture, not one per fixture: the
    # version table is shared, so a config that does not know one owner's
    # revisions cannot resolve its row and would fail before undoing anything.
    version_locations = [_CORE_VERSIONS_DIR] + [
        _owned_versions_dir(plugin) for plugin in [*installed(), *fixtures]
    ]
    config = _config(version_locations, url)
    for revision in ("example_0002_add_extra", "other_0001_create"):
        # Nothing to undo if that plugin never ran in this test.
        with suppress(Exception):
            command.downgrade(config, f"{revision}@base")


def _tables() -> list[str]:
    return inspect(engine).get_table_names()


def _tracked_revisions() -> set[str]:
    with engine.connect() as connection:
        return {
            row[0]
            for row in connection.exec_driver_sql(
                f"select version_num from {VERSION_TABLE}"  # noqa: S608
            )
        }


def test_owns_a_table__true_when_a_versions_folder_sits_next_to_the_plugin_class():
    assert owns_a_table(ExamplePlugin)  # type: ignore[arg-type]


def test_owns_a_table__false_without_a_versions_folder():
    class NoVersionsPlugin:
        name = "NoVersionsPlugin"

    assert not owns_a_table(NoVersionsPlugin)  # type: ignore[arg-type]


def test_migrate_plugin__installs_from_scratch_to_latest():
    migrate(ExamplePlugin)

    assert "example_plugin_assets" in _tables()
    columns = {c["name"] for c in inspect(engine).get_columns("example_plugin_assets")}
    assert "extra" in columns
    assert "example_0002_add_extra" in _tracked_revisions()


def test_migrate_plugin__is_idempotent():
    migrate(ExamplePlugin)

    migrate(ExamplePlugin)  # must not raise on a plugin already at its head

    assert "example_0002_add_extra" in _tracked_revisions()


def test_migrate_all__still_checks_for_orphans_when_a_plugin_is_dropped():
    migrate(ExamplePlugin)

    # Reconciling without ExamplePlugin is what uninstalling it looks like.
    # A literal [] can't be used here: a few of core's own migrations depend
    # on a specific plugin's baseline (see migrations.py's _core_head), so
    # resolving core's own history needs those plugins' directories present
    # regardless - installed() is the smallest list that can.
    with pytest.raises(ValueError, match="belonging to no installed plugin"):
        migrate_all(installed(), engine)


@pytest.mark.parametrize("retired", sorted(RETIRED_PLUGIN_REVISIONS))
def test_migrate_all__forgets_the_revision_of_a_plugin_the_portal_dropped(retired):
    """A database that ran a plugin the portal has since deleted keeps that
    plugin's row. Without reconciling it, the orphan check above would abort
    every later migration, and no core revision could clean it up because the
    check runs first."""
    with engine.begin() as connection:
        connection.execute(_version_table.insert().values(version_num=retired))
    assert retired in _tracked_revisions()

    migrate()

    assert retired not in _tracked_revisions()


def _set_configuration_type(configuration_id, configuration_type) -> None:
    with engine.begin() as connection:
        connection.execute(
            _configuration_table.update()
            .where(_configuration_table.c.id == str(configuration_id))
            .values(configuration_type=configuration_type)
        )


def test_migrate_all__refuses_technical_assets_whose_plugin_is_not_installed():
    asset = TechnicalAssetFactory()
    _set_configuration_type(asset.configuration_id, "GonePlugin")
    try:
        with pytest.raises(
            ValueError, match="no installed plugin provides: GonePlugin"
        ):
            migrate()
    finally:
        _set_configuration_type(
            asset.configuration_id, "FakeTechnicalAssetConfiguration"
        )


def test_migrate_all__ignores_configurations_no_technical_asset_uses():
    orphan = str(uuid4())
    with engine.begin() as connection:
        connection.execute(
            _configuration_table.insert().values(
                id=orphan, configuration_type="GonePlugin"
            )
        )
    try:
        migrate()
    finally:
        with engine.begin() as connection:
            connection.execute(
                _configuration_table.delete().where(_configuration_table.c.id == orphan)
            )


def test_migrate_all__tracks_two_plugins_in_one_shared_version_table():
    """Each plugin is its own Alembic branch, because its first revision has no
    down_revision, so one row per plugin coexists in the single shared table
    alongside core's own."""
    migrate(ExamplePlugin, OtherPlugin)

    assert {"example_0002_add_extra", "other_0001_create"} <= _tracked_revisions()


def test_migrate_all__leaves_other_plugins_alone_when_one_is_reinstalled():
    migrate(ExamplePlugin, OtherPlugin)

    migrate(ExamplePlugin, OtherPlugin)

    tracked = _tracked_revisions()
    assert "example_0002_add_extra" in tracked
    assert "other_0001_create" in tracked


def test_migrate_all__names_the_plugin_whose_row_it_cannot_resolve():
    """The shared version table is the cost of one table instead of one per
    plugin: a row left behind by an uninstalled plugin blocks every plugin's
    migrations, so say so in terms an operator can act on."""
    migrate(ExamplePlugin, OtherPlugin)

    # Reconciling without the example plugin is what uninstalling it looks like.
    with pytest.raises(ValueError, match="belonging to no installed plugin"):
        migrate(OtherPlugin)


def test_migrate_all__skips_plugins_without_a_table():
    class NoTablePlugin(TechnicalAssetPlugin):
        name: ClassVar[str] = "NoTablePlugin"

    migrate(NoTablePlugin)


def test_check_latest_migration__round_trips_the_latest_core_revision():
    url = engine.url.render_as_string(hide_password=False)

    head = check_latest_migration_core(installed(), engine)

    assert head == _core_head(installed(), url)
    assert head in _tracked_revisions()


def test_migrate_all__rolls_back_core_when_a_plugin_migration_fails():
    url = engine.url.render_as_string(hide_password=False)
    config = _config(_version_locations([*installed(), BrokenPlugin]), url)
    head = _core_head(installed(), url)
    previous = ScriptDirectory.from_config(config).get_revision(head).down_revision
    command.downgrade(config, previous)
    try:
        with pytest.raises(ProgrammingError, match="renamed_away"):
            migrate(BrokenPlugin)

        tracked = _tracked_revisions()
        assert previous in tracked
        assert head not in tracked
    finally:
        migrate()


def test_migrate_all__points_at_a_newer_portal_after_rolling_back_the_image():
    newer_core = "ffffffffffff"
    with engine.begin() as connection:
        connection.execute(_version_table.insert().values(version_num=newer_core))
    try:
        with pytest.raises(ValueError, match="newer portal version"):
            migrate()
    finally:
        with engine.begin() as connection:
            connection.execute(
                _version_table.delete().where(
                    _version_table.c.version_num == newer_core
                )
            )


@pytest.fixture
def scratch_engine():
    url = engine.url.set(database=f"{engine.url.database}_concurrent")
    if database_exists(url):
        drop_database(url)
    create_database(url)
    scratch = create_engine(url)
    yield scratch
    scratch.dispose()
    drop_database(url)


def _migrate(target: Engine) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-m", "app.db_tool", "migrate"],
        env={**os.environ, "POSTGRES_DB": str(target.url.database)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _migrate_twice_at_once(target: Engine) -> list[int]:
    runs = [_migrate(target), _migrate(target)]
    return [run.wait(timeout=300) for run in runs]


def _assert_migrated_once(target: Engine) -> None:
    url = target.url.render_as_string(hide_password=False)
    with target.connect() as connection:
        tracked = {
            row[0]
            for row in connection.exec_driver_sql(
                f"select version_num from {VERSION_TABLE}"  # noqa: S608
            )
        }
        services = connection.exec_driver_sql(
            "select count(*) from platform_services where lower(name) = 'parameterstore'"
        ).scalar()
    assert {_core_head(installed(), url), "parameter_store_0001_baseline"} <= tracked
    assert services == 1


def test_migrate_all__two_runs_at_once_on_an_empty_database(scratch_engine):
    assert 0 in _migrate_twice_at_once(scratch_engine)

    assert _migrate(scratch_engine).wait(timeout=300) == 0

    _assert_migrated_once(scratch_engine)


def test_migrate_all__two_runs_at_once_on_an_upgrade(scratch_engine):
    assert _migrate(scratch_engine).wait(timeout=300) == 0
    url = scratch_engine.url.render_as_string(hide_password=False)
    config = _config(_version_locations(installed()), url)
    head = _core_head(installed(), url)
    command.downgrade(config, "parameter_store@base")
    command.downgrade(
        config, ScriptDirectory.from_config(config).get_revision(head).down_revision
    )

    assert 0 in _migrate_twice_at_once(scratch_engine)

    assert _migrate(scratch_engine).wait(timeout=300) == 0

    _assert_migrated_once(scratch_engine)
