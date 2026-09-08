from contextlib import contextmanager
from typing import Iterator
from uuid import UUID

from sqlalchemy.orm import Session


@contextmanager
def as_user(session: Session, user_id: UUID) -> Iterator[None]:
    """Run a block of code as if `user_id` were the authenticated user.

    Service tests call services directly with `session`/`test_session`,
    bypassing `get_db_session` (which normally sets this for real requests).
    Without a `current_user_id`, the DataProduct visibility filter has
    nothing to scope by and raises. Use this to opt in to a real user
    context for the code under test.
    """
    previous_user_id = session.info.get("current_user_id")
    session.info["current_user_id"] = user_id
    try:
        yield
    finally:
        session.info["current_user_id"] = previous_user_id
