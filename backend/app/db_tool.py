from typing import Optional

import typer
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from app.core.helpers.local import add_additional_env_vars

add_additional_env_vars()

from app.core.logging import logger  # noqa: E402
from app.database.database import engine, get_url  # noqa: E402
from app.plugins.migrations import (  # noqa: E402
    check_latest_migration_core,
    migrate_all,
)
from app.plugins.registry import plugin_registry  # noqa: E402
from app.seed import seed_db  # noqa: E402

app = typer.Typer(help="Database migration toolkit for the Data product portal.")


@app.command(name="seed")
def seed_cmd(path: str = typer.Argument(..., help="Path to the seed script.")):
    """
    Seed the data with pregenerated test data
    """
    logger.info(f"Seeding started -> source = {path}")
    seed_db(path)
    logger.info("Seeding finished successfully")


@app.command()
def migrate():
    """
    Migrate database to the latest version.
    """
    logger.info("Migration started")
    try:
        migrate_all(plugin_registry.discovered(), engine)
        logger.info("Migration finished successfully")
    except Exception:
        logger.exception("Something went wrong when migrating")
        exit(1)


@app.command(name="check-latest-migration")
def check_latest_migration_cmd():
    """
    Downgrade the latest core migration by one step and reapply it, to catch
    a malformed upgrade/downgrade pair before it ships.
    """
    logger.info("Checking latest migration")
    try:
        head = check_latest_migration_core(plugin_registry.discovered(), engine)
        logger.info(f"Round-tripped {head} successfully")
    except Exception:
        logger.exception("Migration check failed")
        exit(1)


@app.command()
def init(
    force: bool = typer.Option(
        ...,
        prompt=(
            "Are you sure you want to reinitialize the database?\n"
            "This will drop the entire content of your database."
        ),
        help="Force deletion of the database without confirmation.",
    ),
    seed_path: Optional[str] = typer.Argument(
        default=None, help="Path to a seed script"
    ),
):
    """
    Delete an existing database.
    Reinitialize the database from scratch.
    """
    if force:
        if database_exists(get_url()):
            logger.info(f"Deleting current database {get_url()}")
            drop_database(get_url())
        else:
            logger.info("Database does not exist, not deleting")
        logger.info("Initializing database")
        create_database(get_url())
        migrate()

        if seed_path:
            seed_cmd(seed_path)
    else:
        logger.info("Operation cancelled")


if __name__ == "__main__":
    app()
