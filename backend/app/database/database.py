import time
from contextlib import contextmanager
from typing import Any, Generator, Type, TypeVar
from urllib.parse import quote_plus
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Column, Engine, create_engine, event
from sqlalchemy.orm import Mapper, Query, Session, declarative_base, sessionmaker

from app.core.logging import logger
from app.settings import settings
from app.shared.model import BaseORM
from app.shared.schema import ORMModel

OM = TypeVar("OM", bound=ORMModel)


def ensure_exists(
    id_: UUID, db: Session, type_: Type[OM] | Mapper[Type[OM]], **kwargs
) -> OM:
    item = db.get(type_, id_, **kwargs)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Required item {id_} does not exist",
        )
    return item


def get_url(async_: bool = False) -> str:
    user = quote_plus(settings.POSTGRES_USER)
    password = quote_plus(settings.POSTGRES_PASSWORD)
    return (
        f"postgresql{'+asyncpg' if async_ else ''}://{user}:"
        f"{password}@{settings.POSTGRES_SERVER}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


engine = create_engine(
    get_url(),
    connect_args={"connect_timeout": settings.DB_CONNECT_TIMEOUT_SECONDS},
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT_SECONDS,
    pool_recycle=settings.DB_POOL_RECYCLE_SECONDS,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    pool_use_lifo=True,
)
if settings.OPENTELEMETRY_TRACES_ENABLED:
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    SQLAlchemyInstrumentor().instrument(
        engine=engine,
    )


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, execmany):
    # Tag the start time onto the execution context
    if settings.SLOW_QUERY_LOGGING_ENABLED:
        context._query_start_time = time.perf_counter()


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, execmany):
    if not settings.SLOW_QUERY_LOGGING_ENABLED:
        return
    total_time = time.perf_counter() - context._query_start_time

    # Only log if it exceeds our 500ms threshold
    if total_time >= settings.SLOW_QUERY_THRESHOLD:
        logger.warning(
            f"🐢 SLOW QUERY DETECTED\n"
            f"DURATION: {total_time:.4f}s\n"
            f"STATEMENT: {statement}\n\n"
        )


class MyQuery(Query):
    def get_one(self, primary_key_type: Column, primary_key_value: Any) -> BaseORM:
        result = self.filter(primary_key_type == primary_key_value).all()
        if not result or len(result) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="object not found"
            )
        if len(result) > 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="too many objects returned",
            )
        return result[0]


SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, query_cls=MyQuery
)

Base = declarative_base()


@contextmanager
def db_session() -> Generator[Session]:
    """
    Should not be used directly, use get_db_session instead or get_system_db_session.
    This is a context manager that will commit or rollback the session depending on whether an exception was raised.
    :return:
    """

    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_system_db_session() -> Generator[Session]:
    """
    This session should only be used with caution! Without this the data product visilibity filter will fail.
    So only use it when no user is available. For example in migrations or when running background tasks that are not user specific.
    :return:
    """
    with db_session() as db:
        yield db
