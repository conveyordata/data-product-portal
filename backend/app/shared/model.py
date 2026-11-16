from datetime import date, datetime, timezone

from sqlalchemy import Column, DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import TypeDecorator


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class UTCDateTime(TypeDecorator):
    """Stores UTC without a time zone; aware values are converted, naive ones are taken as UTC."""

    impl = DateTime(timezone=False)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return to_naive_utc(value) if isinstance(value, datetime) else value


def to_naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def naive_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


class BaseORM:
    created_on = Column(UTCDateTime(), server_default=utcnow())
    updated_on = Column(UTCDateTime(), onupdate=utcnow())
