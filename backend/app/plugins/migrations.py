"""Reconciles each registered plugin's own table to the revision it declares.

Design (see SPIKE_NOTES.md for the reasoning):
- One shared runner (alembic_runner/env.py) for every plugin - no per-plugin
  env.py/alembic.ini.
- Each plugin's own `versions/` directory is passed in isolation via
  Alembic's `version_locations` option, so two plugins' histories can never
  collide or produce a confusing multi-head state.
- "One shared table tracks each plugin's currently-applied revision" is
  satisfied by pointing every plugin's Alembic `version_table` at the same
  physical table. Alembic manages that table's rows itself (one row per
  active head); since every plugin's own revision ids are unique strings
  (namespaced by convention, e.g. "azureblob_0001_..."), rows from
  different plugins' histories can coexist in it safely and stay legible.
  The table is created automatically by Alembic the first time it's used -
  no core migration was written for it on purpose.
"""

from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Iterator, Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sdk.plugins.base import TechnicalAssetPlugin
from sqlalchemy import Engine

from app.core.logging import logger

PLUGIN_VERSION_TABLE = "plugin_migration_state"
_RUNNER_DIR = Path(__file__).parent / "alembic_runner"


@contextmanager
def _plugin_config(
    plugin_cls: type[TechnicalAssetPlugin], url: str
) -> Iterator[Config]:
    versions_resource = resources.files(plugin_cls.migrations_package) / "versions"
    with resources.as_file(versions_resource) as versions_dir:
        cfg = Config()
        cfg.set_main_option("script_location", str(_RUNNER_DIR))
        cfg.set_main_option("version_locations", str(versions_dir))
        cfg.set_main_option("sqlalchemy.url", url)
        cfg.attributes["version_table"] = PLUGIN_VERSION_TABLE
        yield cfg


def _current_revision(
    plugin_cls: type[TechnicalAssetPlugin], script: ScriptDirectory, engine: Engine
) -> Optional[str]:
    own_revisions = {r.revision for r in script.walk_revisions()}
    with engine.connect() as connection:
        mc = MigrationContext.configure(
            connection, opts={"version_table": PLUGIN_VERSION_TABLE}
        )
        heads = mc.get_current_heads()
    matches = [h for h in heads if h in own_revisions]
    return matches[0] if matches else None


def reconcile_plugin(plugin_cls: type[TechnicalAssetPlugin], engine: Engine) -> str:
    """Upgrade or downgrade one plugin's table to its declared target_revision."""
    target = plugin_cls.target_revision
    with _plugin_config(
        plugin_cls, engine.url.render_as_string(hide_password=False)
    ) as cfg:
        script = ScriptDirectory.from_config(cfg)
        current = _current_revision(plugin_cls, script, engine)

        if current == target:
            return f"up-to-date at {target}"

        if current is None:
            command.upgrade(cfg, target)
            return f"installed -> {target}"

        ordered = [r.revision for r in script.walk_revisions()]  # head -> base
        if target not in ordered:
            raise ValueError(
                f"Plugin '{plugin_cls.key}' declares unknown target_revision '{target}'"
            )

        if ordered.index(target) < ordered.index(current):
            command.upgrade(cfg, target)
            return f"upgraded {current} -> {target}"
        else:
            command.downgrade(cfg, target)
            return f"downgraded {current} -> {target}"


def reconcile_all(
    plugin_classes: list[type[TechnicalAssetPlugin]], engine: Engine
) -> dict[str, str]:
    """Reconcile every registered plugin's table. Fails loud, like a core migration failure."""
    results: dict[str, str] = {}
    for plugin_cls in plugin_classes:
        logger.info(
            f"Reconciling plugin '{plugin_cls.key}' to {plugin_cls.target_revision}"
        )
        results[plugin_cls.key] = reconcile_plugin(plugin_cls, engine)
    return results
