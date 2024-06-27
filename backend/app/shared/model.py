from sqlalchemy import Column, DateTime
from sqlalchemy_easy_softdelete.mixin import generate_soft_delete_mixin_class
from datetime import datetime
from typing import Callable
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles


class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True


@compiles(utcnow, "postgresql")
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


Base = generate_soft_delete_mixin_class(
    # This table will be ignored by the hook
    # even if the table has the soft-delete column
    # ignored_tables=[IgnoredTable(table_schema="public", name="cars"),]
)  # type: ignore


# Create a Class that inherits from our class builder
class BaseORM(Base):  # type: ignore
    # type hint for autocomplete IDE support
    deleted_at: datetime
    delete: Callable
    undelete: Callable

    created_on = Column(DateTime(timezone=False), server_default=utcnow())
    updated_on = Column(DateTime(timezone=False), onupdate=utcnow())
