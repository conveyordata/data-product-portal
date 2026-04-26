import uuid

from sqlalchemy import Column, Date, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class OutputPortCostRecord(Base):
    __tablename__ = "output_port_cost_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("datasets.id", ondelete="CASCADE"), index=True
    )
    recorded_at = Column(Date, nullable=False, index=True)
    compute_cost = Column(Numeric(12, 4), nullable=False)
    storage_cost = Column(Numeric(12, 4), nullable=False)
    platform_overhead_cost = Column(Numeric(12, 4), nullable=False)

    @property
    def total_cost(self):
        return self.compute_cost + self.storage_cost + self.platform_overhead_cost
