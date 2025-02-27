from sqlalchemy import Column, DateTime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class BaseORM:
    created_on = Column(DateTime(timezone=False), server_default=utcnow())
    updated_on = Column(DateTime(timezone=False), onupdate=utcnow())
