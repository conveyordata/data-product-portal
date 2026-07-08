from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import computed_field

from app.authorization.role_assignments.enums import DecisionStatus
from app.settings import settings
from app.shared.schema import ORMModel


class InputPortBase(ORMModel):
    id: UUID
    justification: str
    status: DecisionStatus
    expires_on: Optional[datetime] = None
    requested_duration_days: Optional[int] = None

    @computed_field
    def is_expiring_soon(self) -> bool:
        if not self.expires_on:
            return False
        return (
            self.expires_on
            - timedelta(days=settings.ACCESS_DURATION_EXPIRING_SOON_DAYS)
            < datetime.now()
        )
