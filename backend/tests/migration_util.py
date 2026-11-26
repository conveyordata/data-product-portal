from contextlib import contextmanager
from typing import Iterator

from alembic import command
from alembic.script import ScriptDirectory

from app.plugins.migrations import (
    _config,
    _version_locations,
    migrate_all,
    owns_a_table,
)
from app.plugins.registry import plugin_registry
from tests import engine


@contextmanager
def before_migration(revision: str) -> Iterator[None]:
    """Downgrades to just before `revision`, lets the test add rows in the old schema, then migrates to head."""
    installed = [p for p in plugin_registry.discovered() if owns_a_table(p)]
    config = _config(
        _version_locations(installed),
        engine.url.render_as_string(hide_password=False),
    )
    previous = ScriptDirectory.from_config(config).get_revision(revision).down_revision
    assert isinstance(previous, str)
    command.downgrade(config, previous)
    try:
        yield
    finally:
        migrate_all(installed, engine)
