import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class OutputPortCostRecord(Base):
    __tablename__ = "output_port_cost_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    recorded_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    compute_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    storage_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    platform_overhead_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False
    )

    @property
    def total_cost(self) -> Decimal:
        return (
            (self.compute_cost or Decimal(0))
            + (self.storage_cost or Decimal(0))
            + (self.platform_overhead_cost or Decimal(0))
        )
