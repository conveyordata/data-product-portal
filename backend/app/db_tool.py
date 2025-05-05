import asyncio
import os

import typer
from alembic import command
from alembic.config import Config
from rich import print
from rich.console import Console
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from app.core.helpers.local import add_additional_env_vars

add_additional_env_vars()

from app.database.database import get_url  # noqa: E402
from app.seed import seed_db  # noqa: E402

app = typer.Typer(help="Database migration toolkit for the Data product portal.")
write_console = Console()


@app.command(name="seed")
def seed_cmd(path: str = typer.Argument(..., help="Path to the seed script.")):
    """
    Seed the data with pregenerated test data
    """
    print("[bold green]Seeding :seedling:[/bold green]")
    print("Seeding started -> source =", path)
    try:
        asyncio.run(seed_db(path))
        print("Seeding finished successfully")
    except Exception as e:
        print("Something went wrong when seeding", e)


@app.command()
def migrate():
    """
    Migrate database to the latest version.
    """
    print("[bold blue]Migration :rocket:[/bold blue]")
    print("Migration started")
    try:
        cfg = Config(
            os.path.join(os.path.dirname(os.path.abspath("__file__")), "alembic.ini")
        )
        command.upgrade(cfg, "heads")
        print("Migration finished successfully")
    except Exception as e:
        print("Something went wrong when migrating", e)
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
    seed_path: str = typer.Argument(default=None, help="Path to a seed script"),
):
    """
    Delete an existing database.
    Reinitialize the database from scratch.
    """
    if force:
        print("[bold red]Deleting :put_litter_in_its_place:[/bold red]")
        if database_exists(get_url()):
            write_console.print(
                f"Deleting current database {get_url()}", highlight=False
            )
            drop_database(get_url())
        else:
            print("Database does not exist, not deleting")
        print("Initializing database")
        create_database(get_url())
        migrate()

        if seed_path:
            seed_cmd(seed_path)
    else:
        print("Operation cancelled")


if __name__ == "__main__":
    app()
