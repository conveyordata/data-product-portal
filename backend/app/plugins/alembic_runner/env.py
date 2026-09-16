"""One Alembic environment shared by every plugin.

A plugin author writes revision files and nothing else: no env.py, no
alembic.ini. Plugins are kept apart from each other through `version_locations`,
which app.plugins.migrations sets per call.
"""

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
target_metadata = None


def run_migrations_online() -> None:
    version_table = config.attributes.get("version_table", "alembic_version")
    connection = config.attributes.get("connection")

    if connection is not None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=version_table,
        )
        with context.begin_transaction():
            context.run_migrations()
        return

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=version_table,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
