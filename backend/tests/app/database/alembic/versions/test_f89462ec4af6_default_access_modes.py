from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy import column, insert, select, table

from tests import engine
from tests.migration_util import before_migration

REVISION = "f89462ec4af6"  # app/database/alembic/versions/2026_11_23_1000-f89462ec4af6_default_access_modes.py

pytestmark = pytest.mark.commits


def test_upgrade__makes_oldest_access_mode_per_type_the_default():
    access_modes = table(
        "access_modes",
        column("id"),
        column("name"),
        column("description"),
        column("technical_asset_types"),
        column("created_on"),
    )
    ids = {name: uuid4() for name in ["newest", "oldest", "middle"]}
    with before_migration(REVISION), engine.begin() as connection:
        connection.execute(
            insert(access_modes),
            [
                {
                    "id": ids["newest"],
                    "name": "newest",
                    "description": "",
                    "technical_asset_types": ["s3", "glue"],
                    "created_on": datetime(2026, 3, 1),
                },
                {
                    "id": ids["oldest"],
                    "name": "oldest",
                    "description": "",
                    "technical_asset_types": ["s3"],
                    "created_on": datetime(2026, 1, 1),
                },
                {
                    "id": ids["middle"],
                    "name": "middle",
                    "description": "",
                    "technical_asset_types": ["glue", "redshift"],
                    "created_on": datetime(2026, 2, 1),
                },
            ],
        )

    defaults = table(
        "default_access_modes",
        column("technical_asset_type"),
        column("access_mode_id"),
    )
    with engine.begin() as connection:
        rows = dict(connection.execute(select(defaults)).all())

    assert rows == {
        "s3": ids["oldest"],
        "glue": ids["middle"],
        "redshift": ids["middle"],
    }
