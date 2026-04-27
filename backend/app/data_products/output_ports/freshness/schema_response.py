from datetime import datetime, time
from uuid import UUID

from app.data_products.output_ports.freshness.enums import FreshnessStatus
from app.shared.schema import ORMModel


class FreshnessSloResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    deadline_time: time
    status: FreshnessStatus
    last_refreshed_at: datetime | None = None
    last_observed_at: datetime | None = None


class FreshnessObservationResponse(ORMModel):
    id: UUID
    output_port_id: UUID
    last_refreshed_at: datetime
    created_at: datetime
    status: FreshnessStatus
