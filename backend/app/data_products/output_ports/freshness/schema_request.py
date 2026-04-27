from datetime import datetime, time

from app.shared.schema import ORMModel


class FreshnessSloRequest(ORMModel):
    deadline_time: time


class FreshnessObservationRequest(ORMModel):
    last_refreshed_at: datetime
