import inspect
import os
from pathlib import Path
from typing import Optional, Sequence

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine

from app.core.logging import logger
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin

VERSION_TABLE = "alembic_version"
_SCRIPT_LOCATION = Path(__file__).parent.parent / "database" / "alembic"
_CORE_VERSIONS_DIR = _SCRIPT_LOCATION / "versions"


def _versions_dir(plugin: type[TechnicalAssetPlugin]) -> Optional[Path]:
    candidate = Path(inspect.getfile(plugin)).parent / "versions"
    return candidate if candidate.is_dir() else None


def owns_a_table(plugin: type[TechnicalAssetPlugin]) -> bool:
    return _versions_dir(plugin) is not None


def _owned_versions_dir(plugin: type[TechnicalAssetPlugin]) -> Path:
    versions_dir = _versions_dir(plugin)
    if versions_dir is None:
        raise ValueError(f"Plugin '{plugin.name}' has no versions folder")
    return versions_dir


def _config(version_locations: Sequence[Path], url: str) -> Config:
    config = Config()
    config.set_main_option("script_location", str(_SCRIPT_LOCATION))
    config.set_main_option("version_path_separator", "os")
    config.set_main_option(
        "version_locations", os.pathsep.join(str(d) for d in version_locations)
    )
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    config.attributes["version_table"] = VERSION_TABLE
    return config


def _current_heads(engine: Engine) -> tuple[str, ...]:
    with engine.connect() as connection:
        return MigrationContext.configure(
            connection, opts={"version_table": VERSION_TABLE}
        ).get_current_heads()


def _own_revisions(plugin: type[TechnicalAssetPlugin], url: str) -> set[str]:
    script = ScriptDirectory.from_config(_config([_owned_versions_dir(plugin)], url))
    return {revision.revision for revision in script.walk_revisions()}


def _own_head(plugin: type[TechnicalAssetPlugin], url: str) -> str:
    script = ScriptDirectory.from_config(_config([_owned_versions_dir(plugin)], url))
    head = script.get_current_head()
    if head is None:
        raise ValueError(
            f"Plugin '{plugin.name}' has no migrations in its versions folder"
        )
    return head


def _core_head(url: str) -> str:
    script = ScriptDirectory.from_config(_config([_CORE_VERSIONS_DIR], url))
    head = script.get_current_head()
    if head is None:
        raise ValueError("Core has no migrations in its own versions folder")
    return head


def migrate_all(
    plugins: Sequence[type[TechnicalAssetPlugin]], engine: Engine
) -> dict[str, str]:
    """Upgrade core and every plugin's own table to the latest revision.

    Core and each plugin are independent Alembic branches sharing one
    version_locations config and one version table: core's history has no
    down_revision on its own first revision, exactly like a plugin's, so
    Alembic resolves and upgrades every branch's head with a single call.
    """
    plugins_owning_tables = [plugin for plugin in plugins if owns_a_table(plugin)]
    url = engine.url.render_as_string(hide_password=False)

    version_locations = [_CORE_VERSIONS_DIR] + [
        _owned_versions_dir(plugin) for plugin in plugins_owning_tables
    ]
    config = _config(version_locations, url)
    script = ScriptDirectory.from_config(config)
    known_revisions = {revision.revision for revision in script.walk_revisions()}

    # The version table is shared, so Alembic resolves every row in it
    # against the revisions this config knows about. A row left behind by a
    # plugin that is no longer installed, or that failed to import, would
    # otherwise fail here as an unreadable "Can't locate revision".
    orphans = [head for head in _current_heads(engine) if head not in known_revisions]
    if orphans:
        raise ValueError(
            f"{VERSION_TABLE} holds revisions belonging to no installed "
            f"plugin: {', '.join(sorted(orphans))}. Reinstall the plugin that "
            f"owns them, or delete those rows from {VERSION_TABLE} to "
            "give up its migration history."
        )

    before = set(_current_heads(engine))

    # Core's head first, then heads: core and a plugin can create the same table and only the plugin's create is guarded, so upgrading everyone to heads in one call could let Alembic run the plugin's create before core's unguarded one and fail on a duplicate table.
    command.upgrade(config, _core_head(url))
    command.upgrade(config, "heads")

    results: dict[str, str] = {}
    for plugin in plugins_owning_tables:
        head = _own_head(plugin, url)
        previous = next((h for h in before if h in _own_revisions(plugin, url)), None)
        if previous == head:
            results[plugin.name] = f"up to date at {head}"
        elif previous is None:
            results[plugin.name] = f"installed at {head}"
        else:
            results[plugin.name] = f"upgraded {previous} to {head}"
        logger.info(f"Reconciled plugin '{plugin.name}': {results[plugin.name]}")

    return results


def check_latest_migration_core(
    plugins: Sequence[type[TechnicalAssetPlugin]], engine: Engine
) -> str:
    """Downgrade core's latest migration by one step, then reapply it.

    A bare `alembic downgrade -1` can't be used for this once any plugin has
    migrated: it only knows core's own script location, not the shared
    version table's plugin rows, and fails to resolve them. This targets
    core's own previous revision through the same shared config migrate_all
    uses, then calls migrate_all to bring everything back.
    """
    plugins_owning_tables = [plugin for plugin in plugins if owns_a_table(plugin)]
    url = engine.url.render_as_string(hide_password=False)

    version_locations = [_CORE_VERSIONS_DIR] + [
        _owned_versions_dir(plugin) for plugin in plugins_owning_tables
    ]
    config = _config(version_locations, url)
    script = ScriptDirectory.from_config(config)

    head = _core_head(url)
    down_revision = script.get_revision(head).down_revision
    if down_revision is not None and not isinstance(down_revision, str):
        raise ValueError(f"Core's latest revision {head} has multiple parents")

    command.downgrade(config, down_revision or "base")
    migrate_all(plugins, engine)
    return head
