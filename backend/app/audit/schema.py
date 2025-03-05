from uuid import UUID

from app.audit.schema_create import AuditLogCreate
from app.users.schema import User


class AuditLog(AuditLogCreate):
    id: UUID
    user: User
