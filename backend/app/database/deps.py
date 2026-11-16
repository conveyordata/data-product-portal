from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_system_db_session
from app.database.visibility import acting_as
from app.users.model import User


def get_db_session(
    session: Session = Depends(get_system_db_session, scope="function"),
    user: User = Depends(get_authenticated_user),
) -> Generator[Session, None, None]:
    with acting_as(session, user.id):
        yield session
