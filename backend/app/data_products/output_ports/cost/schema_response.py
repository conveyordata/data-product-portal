from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import computed_field

from app.shared.schema import ORMModel


class CostRecordResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    recorded_at: date
    compute_cost: Decimal
    storage_cost: Decimal
    platform_overhead_cost: Decimal

    @computed_field
    def total_cost(self) -> Decimal:
        return self.compute_cost + self.storage_cost + self.platform_overhead_cost


class CostHistoryResponse(ORMModel):
    output_port_id: UUID
    records: list[CostRecordResponse]
