from typing import Annotated, Optional
from uuid import UUID

from annotated_types import MinLen

from app.shared.schema import ORMModel


class EphemeralDataProductCreate(ORMModel):
    output_port_ids: Annotated[list[UUID], MinLen(1)]
    ttl_hours: int = 8
    justification: Optional[str] = None
    name: Optional[str] = None


class AddOutputPortsToEphemeral(ORMModel):
    output_port_ids: Annotated[list[UUID], MinLen(1)]
