from contextlib import suppress

import pytest
from alembic import command
from sqlalchemy import inspect

from app.plugins.migrations import (
    _CORE_VERSIONS_DIR,
    RETIRED_PLUGIN_REVISIONS,
    VERSION_TABLE,
    _config,
    _core_head,
    _owned_versions_dir,
    _version_table,
    check_latest_migration_core,
    migrate_all,
    owns_a_table,
)
from app.plugins.registry import plugin_registry
from tests import engine
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


def test_migrate_all__forgets_the_revision_of_a_plugin_the_portal_dropped():
    """A database that ran a plugin the portal has since deleted keeps that
    plugin's row. Without reconciling it, the orphan check above would abort
    every later migration, and no core revision could clean it up because the
    check runs first."""
    retired = next(iter(RETIRED_PLUGIN_REVISIONS))
    with engine.begin() as connection:
        connection.execute(_version_table.insert().values(version_num=retired))
    assert retired in _tracked_revisions()

    migrate()

    assert retired not in _tracked_revisions()


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
    class NoTablePlugin:
        name = "NoTablePlugin"

    migrate(NoTablePlugin)  # type: ignore[arg-type]  # must not raise


def test_check_latest_migration__round_trips_the_latest_core_revision():
    url = engine.url.render_as_string(hide_password=False)

    head = check_latest_migration_core(installed(), engine)

    assert head == _core_head(installed(), url)
    assert head in _tracked_revisions()
