from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.database.database import MyQuery
from app.settings import settings

name = "test_app"


def get_test_url():
    return (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


engine = create_engine(get_test_url())
session_factory = sessionmaker(autoflush=False, bind=engine, query_cls=MyQuery)
TestingSessionLocal = scoped_session(session_factory)

test_session = TestingSessionLocal()
