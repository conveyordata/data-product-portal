import os
from contextlib import ExitStack, contextmanager
from importlib import resources
from pathlib import Path
from typing import Iterator, Sequence

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine

from app.core.logging import logger
from app.technical_asset_configuration.base_schema import TechnicalAssetPlugin

PLUGIN_VERSION_TABLE = "plugin_migration_state"
_RUNNER_DIR = Path(__file__).parent / "alembic_runner"


def owns_a_table(plugin: type[TechnicalAssetPlugin]) -> bool:
    return bool(plugin.target_revision and plugin.migrations_package)


@contextmanager
def _config(
    plugins: Sequence[type[TechnicalAssetPlugin]], url: str
) -> Iterator[Config]:
    with ExitStack() as stack:
        version_locations = [
            str(
                stack.enter_context(
                    resources.as_file(
                        resources.files(plugin.migrations_package) / "versions"
                    )
                )
            )
            for plugin in plugins
        ]
        config = Config()
        config.set_main_option("script_location", str(_RUNNER_DIR))
        config.set_main_option("version_path_separator", "os")
        config.set_main_option("version_locations", os.pathsep.join(version_locations))
        config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
        config.attributes["version_table"] = PLUGIN_VERSION_TABLE
        yield config


def _current_heads(engine: Engine) -> tuple[str, ...]:
    with engine.connect() as connection:
        return MigrationContext.configure(
            connection, opts={"version_table": PLUGIN_VERSION_TABLE}
        ).get_current_heads()


def _base_of(script: ScriptDirectory, revision: str) -> str:
    return list(script.iterate_revisions(revision, "base"))[-1].revision


def _branch_revisions(script: ScriptDirectory, target: str) -> list[str]:
    base = _base_of(script, target)
    return [
        revision.revision
        for revision in script.walk_revisions()
        if _base_of(script, revision.revision) == base
    ]


def _reconcile(
    target: str,
    config: Config,
    script: ScriptDirectory,
    heads: tuple[str, ...],
) -> str:
    own_revisions = _branch_revisions(script, target)
    current = next((head for head in heads if head in own_revisions), None)

    if current == target:
        return f"up to date at {target}"

    if current is None:
        command.upgrade(config, target)
        return f"installed at {target}"

    # own_revisions runs newest first, so a lower index means newer.
    if own_revisions.index(target) < own_revisions.index(current):
        command.upgrade(config, target)
        return f"upgraded {current} to {target}"

    command.downgrade(config, target)
    return f"downgraded {current} to {target}"


def _owns_revision(plugin: type[TechnicalAssetPlugin], url: str) -> bool:
    with _config([plugin], url) as config:
        own_script = ScriptDirectory.from_config(config)
        return plugin.target_revision in {
            revision.revision for revision in own_script.walk_revisions()
        }


def reconcile_all(
    plugins: Sequence[type[TechnicalAssetPlugin]], engine: Engine
) -> dict[str, str]:
    plugins_owning_tables = [plugin for plugin in plugins if owns_a_table(plugin)]
    url = engine.url.render_as_string(hide_password=False)
    results: dict[str, str] = {}

    with _config(plugins_owning_tables, url) as config:
        script = ScriptDirectory.from_config(config)
        known_revisions = {revision.revision for revision in script.walk_revisions()}

        # The version table is shared, so Alembic resolves every row in it
        # against the revisions this config knows about. A row left behind by a
        # plugin that is no longer installed, or that failed to import, would
        # otherwise fail here as an unreadable "Can't locate revision".
        orphans = [
            head for head in _current_heads(engine) if head not in known_revisions
        ]
        if orphans:
            raise ValueError(
                f"{PLUGIN_VERSION_TABLE} holds revisions belonging to no installed "
                f"plugin: {', '.join(sorted(orphans))}. Reinstall the plugin that "
                f"owns them, or delete those rows from {PLUGIN_VERSION_TABLE} to "
                "give up its migration history."
            )

        if not plugins_owning_tables:
            return {}

        for plugin in plugins_owning_tables:
            if not _owns_revision(plugin, url):
                raise ValueError(
                    f"Plugin '{plugin.name}' declares target_revision "
                    f"'{plugin.target_revision}', which is not in its own "
                    "migration history"
                )
            logger.info(
                f"Reconciling plugin '{plugin.name}' to {plugin.target_revision}"
            )
            # owns_a_table above guarantees target_revision is set.
            results[plugin.name] = _reconcile(
                str(plugin.target_revision), config, script, _current_heads(engine)
            )
    return results
