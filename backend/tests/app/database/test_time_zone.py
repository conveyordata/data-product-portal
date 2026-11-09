import re
from pathlib import Path

from sqlalchemy import func, select

import app
from app.database import database

LOCAL_TIME = re.compile(r"datetime\.now\(\)|datetime\.utcnow\(\)|date\.today\(\)")


def test_engine__connections_use_utc():
    with database.engine.connect() as connection:
        assert connection.scalar(select(func.current_setting("TimeZone"))) == "UTC"


def test_app__current_time_is_always_utc():
    offenders = [
        f"{path}:{number}"
        for path in Path(app.__file__).parent.rglob("*.py")
        if "alembic" not in path.parts
        for number, line in enumerate(path.read_text().splitlines(), 1)
        if LOCAL_TIME.search(line)
    ]

    assert offenders == []
