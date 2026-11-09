from datetime import datetime, timezone

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
        if isinstance(value, datetime) and value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value


def naive_utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BaseORM:
    created_on = Column(UTCDateTime(), server_default=utcnow())
    updated_on = Column(UTCDateTime(), onupdate=utcnow())
