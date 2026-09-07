from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_system_db_session
from app.users.model import User


def get_db_session(
    session: Session = Depends(get_system_db_session),
    user: User = Depends(get_authenticated_user),
) -> Generator[Session, None, None]:
    session.info["current_user_id"] = user.id
    try:
        yield session
    finally:
        session.info.pop("current_user_id", None)
