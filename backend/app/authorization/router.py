from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.authorization.schema_response import AccessResponse, IsAdminResponse
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.users.schema import User

router = APIRouter()


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
    resource: Optional[UUID] = Query(None),
    domain: Optional[UUID] = Query(None),
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


@router.get(
    "/admin",
)
def is_admin(
    user: User = Depends(get_authenticated_user),
) -> IsAdminResponse:
    authorizer = Authorization()

    return IsAdminResponse(
        is_admin=authorizer.has_admin_role(user_id=user.id),
        time=user.admin_expiry.isoformat() if user.admin_expiry else None,
    )


_router = router
router = APIRouter(tags=["Authorization"])
router.include_router(_router, prefix="/authz", deprecated=True)
router.include_router(_router, prefix="/v2/authz")
