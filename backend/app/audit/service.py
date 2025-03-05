from typing import Optional
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.audit.model import AuditLog as AuditLogModel
from app.audit.schema_create import AuditLogCreate
from app.core.auth.auth import get_authenticated_user
from app.database.database import get_db_session
from app.users.schema import User


def audit_logs(
    request: Request,
    id: Optional[UUID] = None,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
):
    if request.method != "GET":
        target_id = None
        for param, v in request.query_params.items():
            if param.endswith("_id"):
                target_id = v
        for param, v in request.path_params.items():
            if param.endswith("_id"):
                target_id = v
        log_entry = AuditLogCreate(
            user_id=user.id,
            action=request.scope["route"].name,
            subject_id=id,
            target_id=target_id,
            status_code=-1,
        )
        log = AuditLogModel(**log_entry.model_dump())
        db.add(log)
        db.commit()
        request.state.audit_id = log.id
        print("State 1: ", request.state.audit_id)
    yield
