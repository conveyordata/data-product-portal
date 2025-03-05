from typing import Optional
from uuid import UUID

from app.audit.model import AuditLog as AuditLogModel
from app.shared.schema import ORMModel


class AuditLogCreate(ORMModel):
    action: str
    subject_id: Optional[UUID] = None
    target_id: Optional[UUID] = None
    user_id: UUID
    status_code: int
    ip: str
    user_agent: Optional[str] = None
    response: Optional[str] = None
    query_parameters: Optional[str] = None
    path_parameters: Optional[str] = None

    class Meta:
        orm_model = AuditLogModel


class AuditLogUpdate(AuditLogCreate):
    pass
