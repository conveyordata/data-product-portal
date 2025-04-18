from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.database import database

name = "test_app"


engine = create_engine(database.get_url())
session_factory = sessionmaker(autoflush=False, bind=engine, query_cls=database.MyQuery)
TestingSessionLocal = scoped_session(session_factory)

test_session = TestingSessionLocal()
