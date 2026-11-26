from uuid import uuid4

import pytest
from sqlalchemy import column, delete, insert, select, table

from tests import engine
from tests.migration_util import before_migration

REVISION = "3d9c51e0a7b2"  # app/database/alembic/versions/2026_10_19_1200-3d9c51e0a7b2_add_domain_namespace_status_finalizers.py

pytestmark = pytest.mark.commits


def test_upgrade__backfills_unique_namespaces_from_names():
    with before_migration(REVISION):
        # One transaction per row so created_on, and thus suffix order, differs
        for name in ["Risk & Compliance", "risk & compliance", "!!!", "..", "Sales"]:
            with engine.begin() as connection:
                connection.execute(
                    insert(table("domains", column("id"), column("name"))).values(
                        id=uuid4(), name=name
                    )
                )

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
