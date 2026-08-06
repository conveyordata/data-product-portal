from typing import Optional
from uuid import UUID

from app.shared.schema import ORMModel


class FinalizerRequest(ORMModel):
    finalizer: str


class RequestInputPortsForAbstractDataProductRequestItem(ORMModel):
    output_port_id: UUID
    access_mode_id: Optional[UUID] = None
