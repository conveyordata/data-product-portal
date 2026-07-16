from datetime import datetime
from typing import Optional
from uuid import UUID

from app.abstract_data_product.input_ports.enums import InputPortStatus, RenewalStatus
from app.authorization.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class InputPortRequestBase(ORMModel):
    id: UUID
    justification: str
    decision_note: Optional[str] = None
    valid_until: Optional[datetime]
    requested_by: User
    decided_by: Optional[User] = None
    decision: DecisionStatus
    created_on: datetime
    requested_on: datetime


class InputPortBase(ORMModel):
    id: UUID
    status: InputPortStatus
    # This the current request
    # When you have an initial output port request this will be the pending one
    # When there is an active approved request it will be that
    # No active approved request, and latest is declined it will be declined
    # When the latest is approved but expired it will return that one
    current_request: InputPortRequestBase
    renewal_status: Optional[RenewalStatus] = None
