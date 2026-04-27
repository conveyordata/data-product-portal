import uuid
from datetime import datetime, time

from sqlalchemy import ForeignKey, Time, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.shared.model import utcnow


class FreshnessSlo(Base):
    __tablename__ = "output_port_freshness_slos"
    __table_args__ = (UniqueConstraint("output_port_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    deadline_time: Mapped[time] = mapped_column(Time(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(), onupdate=utcnow(), nullable=False
    )


class FreshnessObservation(Base):
    __tablename__ = "output_port_freshness_observations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    last_refreshed_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=utcnow(), nullable=False
    )
