from uuid import uuid4

from alembic import command
from sqlalchemy import column, delete, insert, select, table

from app.plugins.migrations import (
    _config,
    _version_locations,
    migrate_all,
    owns_a_table,
)
from app.plugins.registry import plugin_registry
from tests import engine

PREVIOUS = "a82c9b3e7d41"


def test_migration__backfills_unique_namespaces_from_names():
    url = engine.url.render_as_string(hide_password=False)
    installed = [p for p in plugin_registry.discovered() if owns_a_table(p)]
    config = _config(_version_locations(installed), url)
    command.downgrade(config, PREVIOUS)
    try:
        # One transaction per row so created_on, and thus suffix order, differs
        for name in ["Risk & Compliance", "risk & compliance", "!!!", "..", "Sales"]:
            with engine.begin() as connection:
                connection.execute(
                    insert(table("domains", column("id"), column("name"))).values(
                        id=uuid4(), name=name
                    )
                )
    finally:
        migrate_all(installed, engine)

    domains = table(
        "domains",
        column("id"),
        column("name"),
        column("namespace"),
        column("status"),
        column("finalizers"),
    )
    with engine.begin() as connection:
        rows = connection.execute(select(domains)).all()
        connection.execute(delete(domains))

    by_name = {name: (id_, ns, st, fin) for id_, name, ns, st, fin in rows}
    assert by_name["Risk & Compliance"][1] == "risk--compliance"
    assert by_name["risk & compliance"][1] == "risk--compliance-2"
    assert by_name["!!!"][1] == str(by_name["!!!"][0])
    assert by_name[".."][1] == str(by_name[".."][0])
    assert by_name["Sales"][1:] == ("sales", "active", [])
