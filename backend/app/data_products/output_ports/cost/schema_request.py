from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import Field

from app.shared.schema import ORMModel


class CreateCostRecord(ORMModel):
    recorded_at: Optional[date] = None  # defaults to today server-side if omitted
    compute_cost: Decimal = Field(ge=0)
    storage_cost: Decimal = Field(ge=0)
    platform_overhead_cost: Decimal = Field(ge=0)
