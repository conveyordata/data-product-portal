import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column as SQLColumn
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_contracts.schema.model import Schema as SchemaModel


class Column(Base, BaseORM):
    __tablename__ = "columns"
    id = SQLColumn(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    schema_id: Mapped[UUID] = mapped_column(ForeignKey("schemas.id"))
    name = SQLColumn(String)
    description = SQLColumn(String)
    data_type = SQLColumn(String)
    checks = SQLColumn(String)

    schema: Mapped["SchemaModel"] = relationship("Schema", back_populates="columns")
