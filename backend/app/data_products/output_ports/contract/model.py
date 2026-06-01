import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, SmallInteger, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class OutputPortSchemaObject(Base):
    __tablename__ = "output_port_schema_objects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    logical_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    physical_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    physical_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)


class OutputPortSchemaProperty(Base):
    __tablename__ = "output_port_schema_properties"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    schema_object_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("output_port_schema_objects.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_property_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("output_port_schema_properties.id", ondelete="CASCADE"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    business_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logical_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_key: Mapped[bool] = mapped_column(Boolean, default=False)
    unique: Mapped[bool] = mapped_column(Boolean, default=False)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    partitioned: Mapped[bool] = mapped_column(Boolean, default=False)
    partition_key_position: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )
    primary_key_position: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True
    )
    physical_type: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    examples: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0)
