import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import utcnow


class DataQualityTechnicalAsset(Base):
    """
    We store the data quality for technical assets in a separate table instead of linking to technical assets table.
    The reason for this is that creating an exact link will be difficult to always achieve.
    By storing it this way we have the information, and we can see whether creating a link might be feasible in the future
    or we need to clean/validate the provided input.
    """

    __tablename__ = "data_quality_technical_assets"

    name: Mapped[str] = mapped_column(String(length=255), primary_key=True)
    status: Mapped[str] = mapped_column(
        Text,
        default="unknown",
        nullable=False,
    )

    # Relationships
    data_quality_summary_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("output_port_data_quality_summaries.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    data_quality_summary: Mapped["DataQualitySummary"] = relationship(
        lazy="raise", back_populates="technical_assets"
    )


class DataQualitySummary(Base):
    __tablename__ = "output_port_data_quality_summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    details_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=utcnow(), nullable=False
    )
    overall_status: Mapped[str] = mapped_column(
        Text,
        default="unknown",
        nullable=False,
    )
    assets_with_checks: Mapped[int] = mapped_column(SmallInteger, default=0)
    assets_with_issues: Mapped[int] = mapped_column(SmallInteger, default=0)
    dimensions = Column(JSONB, nullable=True)

    # Relationships
    technical_assets: Mapped[list["DataQualityTechnicalAsset"]] = relationship(
        lazy="joined",
        cascade="all, delete-orphan",
        back_populates="data_quality_summary",  # We need all summary info when querying
    )
