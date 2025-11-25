import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import utcnow

if TYPE_CHECKING:
    from app.datasets.model import Dataset


class DatasetCuratedQuery(Base):
    __tablename__ = "dataset_curated_queries"

    curated_query_id: Mapped[uuid.UUID] = mapped_column(
        "curated_query_id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=utcnow())

    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="curated_queries",
    )
