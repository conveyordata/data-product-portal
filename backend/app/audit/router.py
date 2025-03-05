from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.schema import AuditLog
from app.audit.service import AuditLogService
from app.database.database import get_db_session
from app.dependencies import only_for_admin

router = APIRouter(prefix="/audit_logs", tags=["audit_logs"])


@router.get("", dependencies=[Depends(only_for_admin)])
def get_audit_logs(
    db: Session = Depends(get_db_session),
) -> list[AuditLog]:
    return AuditLogService().get_audit_logs(db)


@router.get("/{id}", dependencies=[Depends(only_for_admin)])
def get_audit_log(id: UUID, db: Session = Depends(get_db_session)) -> AuditLog:
    return AuditLogService().get_audit_log(id, db)
