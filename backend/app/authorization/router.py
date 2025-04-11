from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends

from app.authorization.schema import AccessResponse
from app.core.auth.auth import get_authenticated_user
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.users.schema import User

router = APIRouter(prefix="/authz", tags=["authz"])


@router.get(
    "/access/{action}",
    responses={
        200: {
            "description": "Access check result",
            "content": {
                "application/json": {"access": "true"},
            },
        },
    },
)
def check_access(
    action: AuthorizationAction,
    resource: Optional[UUID] = None,
    domain: Optional[UUID] = None,
    user: User = Depends(get_authenticated_user),
) -> AccessResponse:
    """Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.
    """
    sub = str(user.id)
    dom = "*" if domain is None else str(domain)
    obj = "*" if resource is None else str(resource)

    authorizer = Authorization()
    result = authorizer.has_access(sub=sub, dom=dom, obj=obj, act=action)
    return AccessResponse(allowed=result)
