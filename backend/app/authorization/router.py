from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.authorization.schema import AccessResponse, IsAdminResponse
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.database.database import get_db_session
from app.roles import ADMIN_UUID
from app.users.schema import User

router = APIRouter(prefix="/authz", tags=["authz"])


@router.get(
    "/access/{action}",
    responses={
        200: {
            "description": "Access check result",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {"access": {"type": "boolean"}},
                    }
                }
            },
        },
    },
)
def check_access(
    action: Action,
    resource: Optional[UUID] = None,
    domain: Optional[UUID] = None,
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> AccessResponse:
    """Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.
    """
    sub = str(user.id)
    dom = "*" if domain is None else str(domain)
    obj = "*" if resource is None else str(resource)

    authorizer = Authorization()

    # Check if user has admin creds and if they are still valid
    if user.admin_expiry:
        if user.admin_expiry <= datetime.now(tz=timezone.utc).replace(tzinfo=None):
            authorizer.revoke_global_role(user_id=user.id, role_id=ADMIN_UUID)

    result = authorizer.has_access(sub=sub, dom=dom, obj=obj, act=action)
    return AccessResponse(allowed=result)


@router.get(
    "/admin",
    responses={
        200: {
            "description": "Admin role assignment",
            "content": {"application/json": {"schema": {"type": "boolean"}}},
        },
    },
)
def is_admin(
    user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> IsAdminResponse:
    authorizer = Authorization()
    if user.admin_expiry:
        if user.admin_expiry <= datetime.now(tz=timezone.utc).replace(tzinfo=None):
            authorizer.revoke_admin_role(user_id=user.id)
    return IsAdminResponse(
        is_admin=authorizer.has_admin_role(user_id=user.id),
        time=user.admin_expiry.isoformat() if user.admin_expiry else None,
    )
