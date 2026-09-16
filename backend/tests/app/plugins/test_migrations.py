from contextlib import suppress

import pytest
from alembic import command
from sqlalchemy import inspect

from app.plugins.migrations import (
    PLUGIN_VERSION_TABLE,
    _config,
    owns_a_table,
    reconcile_all,
)
from app.plugins.registry import plugin_registry
from tests import engine


def installed() -> list:
    """The plugins the portal itself would reconcile, e.g. S3.

    reconcile_all is always called with every installed plugin, because the
    version table is shared and Alembic resolves every row in it. Passing a
    subset is what an uninstalled plugin looks like, which is its own test.
    """
    return [p for p in plugin_registry.discovered() if owns_a_table(p)]


def reconcile(*plugins) -> dict:
    return reconcile_all([*installed(), *plugins], engine)


class FakePlugin:
    """Enough of a plugin for the reconciler: a name, a target, and revisions.

    Deliberately not a TechnicalAssetPlugin subclass, so these fixtures never
    show up in plugin discovery. Hence the type: ignore at the call sites.
    """

    def __init__(self, name: str, migrations_package: str, target_revision: str):
        self.name = name
        self.migrations_package = migrations_package
        self.target_revision = target_revision


def example_plugin(target_revision: str = "example_0002_add_extra") -> FakePlugin:
    return FakePlugin("ExamplePlugin", "tests.fixtures.example_plugin", target_revision)


def other_plugin() -> FakePlugin:
    return FakePlugin("OtherPlugin", "tests.fixtures.other_plugin", "other_0001_create")


@pytest.fixture(autouse=True)
def _clean_fixture_plugins():
    yield
    fixtures = [example_plugin(), other_plugin()]
    url = engine.url.render_as_string(hide_password=False)
    # One config covering every fixture, not one per fixture: the version table
    # is shared, so a config that does not know one fixture's revisions cannot
    # resolve its row and would fail before undoing anything.
    with _config([*installed(), *fixtures], url) as config:  # type: ignore[list-item]
        for plugin in fixtures:
            # Nothing to undo if that plugin never ran in this test.
            with suppress(Exception):
                command.downgrade(config, f"{plugin.target_revision}@base")


def _tables() -> list[str]:
    return inspect(engine).get_table_names()


def _tracked_revisions() -> set[str]:
    with engine.connect() as connection:
        return {
            row[0]
            for row in connection.exec_driver_sql(
                f"select version_num from {PLUGIN_VERSION_TABLE}"  # noqa: S608
            )
        }


def test_reconcile_plugin__installs_from_scratch():
    outcome = reconcile(example_plugin("example_0001_create"))["ExamplePlugin"]

    assert outcome == "installed at example_0001_create"
    assert "example_plugin_assets" in _tables()


def test_reconcile_plugin__upgrades_to_target():
    reconcile(example_plugin("example_0001_create"))["ExamplePlugin"]

    outcome = reconcile(example_plugin("example_0002_add_extra"))["ExamplePlugin"]

    assert outcome == "upgraded example_0001_create to example_0002_add_extra"
    columns = {c["name"] for c in inspect(engine).get_columns("example_plugin_assets")}
    assert "extra" in columns


def test_reconcile_plugin__downgrades_when_target_is_older():
    reconcile(example_plugin("example_0002_add_extra"))["ExamplePlugin"]

    outcome = reconcile(example_plugin("example_0001_create"))["ExamplePlugin"]

    assert outcome == "downgraded example_0002_add_extra to example_0001_create"
    columns = {c["name"] for c in inspect(engine).get_columns("example_plugin_assets")}
    assert "extra" not in columns


def test_reconcile_plugin__is_idempotent():
    reconcile(example_plugin())["ExamplePlugin"]

    outcome = reconcile(example_plugin())["ExamplePlugin"]

    assert outcome == "up to date at example_0002_add_extra"


def test_reconcile_all__rejects_unknown_target_revision():
    with pytest.raises(ValueError, match="not in its own migration history"):
        reconcile(example_plugin("example_0099_does_not_exist"))


def test_reconcile_all__tracks_two_plugins_in_one_shared_version_table():
    """Each plugin is its own Alembic branch, because its first revision has no
    down_revision, so one row per plugin coexists in the single shared table."""
    results = reconcile(example_plugin(), other_plugin())

    assert results["ExamplePlugin"] == "installed at example_0002_add_extra"
    assert results["OtherPlugin"] == "installed at other_0001_create"
    assert {"example_0002_add_extra", "other_0001_create"} <= _tracked_revisions()


def test_reconcile_all__leaves_other_plugins_alone_when_one_moves():
    reconcile(example_plugin(), other_plugin())

    reconcile(example_plugin("example_0001_create"), other_plugin())

    tracked = _tracked_revisions()
    assert "example_0001_create" in tracked
    assert "other_0001_create" in tracked


def test_reconcile_all__names_the_plugin_whose_row_it_cannot_resolve():
    """The shared version table is the cost of one table instead of one per
    plugin: a row left behind by an uninstalled plugin blocks every plugin's
    migrations, so say so in terms an operator can act on."""
    reconcile(example_plugin(), other_plugin())

    # Reconciling without the example plugin is what uninstalling it looks like.
    with pytest.raises(ValueError, match="belonging to no installed plugin"):
        reconcile(other_plugin())


def test_reconcile_all__skips_plugins_without_a_table():
    class PluginWithoutTable:
        name = "NoTablePlugin"
        target_revision = None
        migrations_package = None

    assert reconcile_all([PluginWithoutTable()], engine) == {}  # type: ignore[list-item]
