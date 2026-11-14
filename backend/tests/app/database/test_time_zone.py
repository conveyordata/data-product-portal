import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import func, select

import app
from tests.factories import UserFactory

LOCAL_TIME = re.compile(r"datetime\.now\(\)|datetime\.utcnow\(\)|date\.today\(\)")
NAIVE_COLUMN = re.compile(r"\bDateTime\((timezone=False)?\)")


def test_utc_date_time__stores_aware_values_as_utc_whatever_the_session_time_zone(
    session,
):
    user = UserFactory()
    session.execute(select(func.set_config("TimeZone", "Europe/Brussels", True)))

    user.admin_expiry = datetime(2099, 1, 1, 2, 0, tzinfo=timezone(timedelta(hours=2)))
    session.flush()
    session.refresh(user)

    assert user.admin_expiry == datetime(2099, 1, 1, 0, 0)


def test_app__current_time_is_always_utc():
    assert _lines_matching(LOCAL_TIME) == []


def test_app__columns_without_time_zone_use_utc_date_time():
    assert _lines_matching(NAIVE_COLUMN, exclude=("shared/model.py",)) == []


def _lines_matching(pattern, exclude=()):
    return [
        f"{path}:{number}"
        for path in Path(app.__file__).parent.rglob("*.py")
        if "alembic" not in path.parts and not any(map(path.match, exclude))
        for number, line in enumerate(path.read_text().splitlines(), 1)
        if pattern.search(line)
    ]
