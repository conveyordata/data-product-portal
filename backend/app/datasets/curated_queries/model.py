import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base
from app.shared.model import utcnow


class DatasetCuratedQuery(Base):
    __tablename__ = "dataset_curated_queries"

    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, primary_key=True, default=0, nullable=False
    )
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=utcnow()
    )
