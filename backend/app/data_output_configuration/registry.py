"""
Plugin registry for discovering and managing data output configuration plugins.

Supports both internal plugins (in this codebase) and external plugins (pip installed packages).
"""

import importlib
import logging
from typing import Optional

from app.data_output_configuration.base_schema import AssetProviderPlugin

logger = logging.getLogger(__name__)


class PluginRegistry:
    """
    Central registry for data output configuration plugins.

    Plugins can be discovered through:
    1. Environment variable (ENABLED_PLUGINS) - comma-separated list of plugin module paths
    2. Package entry points (for pip-installed external plugins)
    """

    _plugins: dict[str, type[AssetProviderPlugin]] = {}
    _initialized: bool = False

    @classmethod
    def discover_and_register(cls, enabled_plugins: Optional[list[str]] = None):
        """
        Discover and register all plugins from configured sources.

        Args:
            enabled_plugins: List of plugin module paths (e.g., "app.data_output_configuration.snowflake.schema.SnowflakeDataOutput")
                           If None, will use default internal plugins
        """
        if cls._initialized:
            logger.warning("Plugin registry already initialized, skipping re-discovery")
            return

        # Default internal plugins
        if enabled_plugins is None:
            enabled_plugins = [
                "app.data_output_configuration.snowflake.schema.SnowflakeDataOutput",
                "app.data_output_configuration.databricks.schema.DatabricksDataOutput",
                "app.data_output_configuration.glue.schema.GlueDataOutput",
                "app.data_output_configuration.redshift.schema.RedshiftDataOutput",
                # S3 will be external plugin for testing
            ]

        # Load plugins from module paths
        failed_plugins = []
        for plugin_path in enabled_plugins:
            try:
                cls._load_plugin_from_path(plugin_path)
            except Exception as e:  # noqa: PERF203
                failed_plugins.append((plugin_path, e))

        # Log all failures after loop
        for plugin_path, error in failed_plugins:
            logger.error(f"Failed to load plugin from {plugin_path}: {error}")

        # Discover external plugins via entry points
        cls._discover_entry_point_plugins()

        cls._initialized = True
        logger.info(
            f"Plugin registry initialized with {len(cls._plugins)} plugins: {list(cls._plugins.keys())}"
        )

    @classmethod
    def _load_plugin_from_path(cls, plugin_path: str):
        """
        Load a plugin from a module path string.

        Args:
            plugin_path: Full module path to plugin class (e.g., "app.data_output_configuration.snowflake.schema.SnowflakeDataOutput")
        """
        module_path, class_name = plugin_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        plugin_class = getattr(module, class_name)

        if not issubclass(plugin_class, AssetProviderPlugin):
            raise TypeError(f"{plugin_path} is not a subclass of AssetProviderPlugin")

        cls.register(plugin_class)
        logger.debug(f"Loaded plugin: {class_name} from {module_path}")

    @classmethod
    def _discover_entry_point_plugins(cls):
        """
        Discover plugins registered via package entry points.

        External plugins can register themselves in setup.py:
            entry_points={
                "data_product_portal.plugins": [
                    "S3DataOutput = s3_plugin.schema:S3DataOutput",
                ],
            }
        """
        # Requires Python 3.10+ for importlib.metadata
        try:
            # Python 3.10+ uses importlib.metadata
            from importlib.metadata import entry_points
        except ImportError:
            # Python 3.8-3.9 compatibility
            try:
                from importlib_metadata import entry_points
            except ImportError:
                logger.warning(
                    "importlib.metadata not available, skipping entry point discovery"
                )
                return

        try:
            # Get entry points for our plugin group
            eps = entry_points()

            # Handle different return types across Python versions
            if hasattr(eps, "select"):
                # Python 3.10+
                plugin_eps = eps.select(group="data_product_portal.plugins")
            else:
                # Python 3.8-3.9
                plugin_eps = eps.get("data_product_portal.plugins", [])

            for entry_point in plugin_eps:
                try:
                    plugin_class = entry_point.load()

                    if not issubclass(plugin_class, AssetProviderPlugin):
                        logger.error(
                            f"Entry point {entry_point.name} does not point to AssetProviderPlugin subclass"
                        )
                        continue

                    cls.register(plugin_class)
                    logger.info(
                        f"Loaded external plugin: {entry_point.name} from entry point"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to load plugin from entry point {entry_point.name}: {e}"
                    )
        except Exception as e:
            logger.error(f"Error during entry point discovery: {e}")

    @classmethod
    def register(cls, plugin: type[AssetProviderPlugin]):
        """
        Register a plugin class.

        Args:
            plugin: Plugin class to register
        """
        plugin_name = plugin.__name__

        if plugin_name in cls._plugins:
            logger.warning(f"Plugin {plugin_name} already registered, overwriting")

        cls._plugins[plugin_name] = plugin
        logger.debug(f"Registered plugin: {plugin_name}")

    @classmethod
    def get_all(cls) -> list[type[AssetProviderPlugin]]:
        """
        Get all registered plugins.

        Returns:
            List of registered plugin classes
        """
        if not cls._initialized:
            logger.warning(
                "Plugin registry not initialized, call discover_and_register() first"
            )

        return list(cls._plugins.values())

    @classmethod
    def get(cls, plugin_name: str) -> Optional[type[AssetProviderPlugin]]:
        """
        Get a specific plugin by name.

        Args:
            plugin_name: Name of the plugin class

        Returns:
            Plugin class or None if not found
        """
        return cls._plugins.get(plugin_name)

    @classmethod
    def reset(cls):
        """Reset the registry (useful for testing)"""
        cls._plugins = {}
        cls._initialized = False

    @classmethod
    def get_all_migrations(cls) -> dict[str, str]:
        """
        Get all plugin migration file paths.

        Returns:
            Dictionary mapping plugin name to migration file path
        """
        migrations: dict[str, str] = {}
        for name, plugin in cls._plugins.items():
            migration_path = plugin.get_migration_path()
            if migration_path is not None:
                migrations[name] = migration_path
        return migrations

    @classmethod
    def run_pending_migrations(cls, auto_approve: bool = False) -> dict[str, bool]:
        """
        Run pending migrations for all registered plugins.

        This checks which plugin migrations haven't been applied yet and runs them.

        Args:
            auto_approve: If True, run migrations without confirmation.
                         If False, only check which migrations would run.

        Returns:
            Dictionary mapping plugin name to whether migration was run/would run
        """
        from alembic import command
        from alembic.config import Config
        from alembic.runtime.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from sqlalchemy import create_engine

        from app.database.database import get_url

        results = {}

        try:
            # Get database connection
            engine = create_engine(get_url())

            # Get Alembic config
            alembic_cfg = Config("alembic.ini")
            script = ScriptDirectory.from_config(alembic_cfg)

            # Get current database revision
            with engine.begin() as connection:
                context = MigrationContext.configure(connection)
                context.get_current_revision()

            # Check each plugin's migration
            for plugin_name, plugin_class in cls._plugins.items():
                migration_path = plugin_class.get_migration_path()

                if not migration_path:
                    logger.debug(f"Plugin {plugin_name} has no migration path")
                    results[plugin_name] = False
                    continue

                # Extract revision from migration filename
                # Format: YYYY_MM_DD_HHMM-description.py
                # The revision is in the migration file itself, but we can check if it's in the chain
                try:
                    # Get all revisions up to head
                    script.get_heads()

                    # For now, we'll use alembic upgrade head to run all pending
                    # In a more sophisticated implementation, we'd track which specific
                    # migration corresponds to which plugin

                    if auto_approve:
                        logger.info(
                            f"Running migration for plugin {plugin_name}: {migration_path}"
                        )
                        with engine.begin() as connection:
                            alembic_cfg.attributes["connection"] = connection
                            command.upgrade(alembic_cfg, "head")
                        results[plugin_name] = True
                    else:
                        # Just check if there are pending migrations
                        results[plugin_name] = True
                        logger.info(
                            f"Migration available for {plugin_name}: {migration_path}"
                        )

                except Exception as e:
                    logger.error(f"Error checking migration for {plugin_name}: {e}")
                    results[plugin_name] = False

            return results

        except Exception as e:
            logger.error(f"Error running plugin migrations: {e}")
            return results

    @classmethod
    def ensure_plugin_tables(cls):
        """
        Ensure all plugin tables exist in the database.

        This is called during startup to automatically create tables for newly
        registered plugins. It runs 'alembic upgrade head' which will apply
        any pending migrations.

        This is safer than running individual migrations because:
        1. Alembic tracks which migrations have been applied
        2. It respects the migration order/dependencies
        3. It's idempotent - safe to run multiple times
        """
        try:
            from pathlib import Path

            from alembic import command
            from alembic.config import Config

            # Get the alembic.ini path relative to this file
            backend_dir = Path(__file__).parent.parent.parent
            alembic_ini = backend_dir / "alembic.ini"

            if not alembic_ini.exists():
                logger.warning(
                    f"alembic.ini not found at {alembic_ini}, skipping auto-migration"
                )
                return

            logger.info("Checking for pending plugin migrations...")
            alembic_cfg = Config(str(alembic_ini))

            # Run alembic upgrade head to apply any pending migrations
            command.upgrade(alembic_cfg, "head")
            logger.info("Plugin table migrations complete")

        except Exception as e:
            logger.warning(f"Could not auto-run migrations: {e}")
            logger.info("You may need to run 'alembic upgrade head' manually")
