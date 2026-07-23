from datetime import date, datetime
from typing import Optional
from uuid import UUID

from app.abstract_data_product.input_ports.enums import (
    InputPortRequestDecision,
    InputPortStatus,
    RenewalStatus,
)
from app.shared.schema import ORMModel
from app.users.schema import User


class InputPortRequestBase(ORMModel):
    id: UUID
    justification: str
    decision_note: Optional[str] = None
    valid_until: Optional[date]
    requested_by: User
    decided_by: Optional[User] = None
    decision: InputPortRequestDecision
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[User] = None
    created_on: datetime
    requested_on: datetime


class InputPortBase(ORMModel):
    id: UUID
    status: InputPortStatus
    current_request: InputPortRequestBase
    renewal_status: Optional[RenewalStatus] = None
