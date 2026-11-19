from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import AuthenticatedUser
from app.database.database import SystemDbSession
from app.database.visibility import acting_as


def get_db_session(
    session: SystemDbSession, user: AuthenticatedUser
) -> Generator[Session, None, None]:
    with acting_as(session, user.id):
        yield session


DbSession = Annotated[Session, Depends(get_db_session, scope="function")]
