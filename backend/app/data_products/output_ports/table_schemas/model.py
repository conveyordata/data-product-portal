import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.configuration.tags.model import Tag
from app.database.database import Base
from app.shared.model import utcnow

tag_output_port_table_schema_table = Table(
    "tags_output_port_table_schemas",
    Base.metadata,
    Column("table_schema_id", ForeignKey("output_port_table_schemas.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)

tag_output_port_column_table = Table(
    "tags_output_port_columns",
    Base.metadata,
    Column("column_id", ForeignKey("output_port_columns.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


class OutputPortTableSchema(Base):
    __tablename__ = "output_port_table_schemas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_output_port_table_schema_table, lazy="joined"
    )
    columns: Mapped[list["OutputPortColumn"]] = relationship(
        back_populates="table_schema",
        cascade="all, delete-orphan",
        lazy="joined",
        order_by="OutputPortColumn.name",
    )


class OutputPortColumn(Base):
    __tablename__ = "output_port_columns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    table_schema_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("output_port_table_schemas.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    data_type: Mapped[str | None] = mapped_column(String, nullable=True)

    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_output_port_column_table, lazy="joined"
    )
    table_schema: Mapped["OutputPortTableSchema"] = relationship(
        back_populates="columns", lazy="raise"
    )
