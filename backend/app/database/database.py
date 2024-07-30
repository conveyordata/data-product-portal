from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Column, create_engine
from sqlalchemy.orm import Query, Session, declarative_base, sessionmaker

from app.settings import settings
from app.shared.model import BaseORM
from app.shared.schema import ORMModel


def ensure_exists(id: UUID, db: Session, type: type[BaseORM]) -> ORMModel:
    item = db.get(type, id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Required item {id} does not exist",
        )
    return item


def get_url():
    return (
        f"postgresql://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


engine = create_engine(get_url(), connect_args={})


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


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
