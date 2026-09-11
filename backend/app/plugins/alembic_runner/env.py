"""One generic Alembic env.py, shared by every plugin.

A plugin author never writes an env.py or alembic.ini - only `versions/*.py`
revision files. Isolation between plugins comes from `version_locations`
(set per call in app.plugins.migrations), not from a separate env.py per
plugin - Alembic supports pointing one script environment's version-file
directory at any location, independent of where env.py itself lives.
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

    config_section = config.get_section(config.config_ini_section, {})
    connectable = engine_from_config(
        config_section, prefix="sqlalchemy.", poolclass=pool.NullPool
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
