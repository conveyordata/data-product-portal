from fastapi import APIRouter, Depends

from app.authorization.schema import AccessRequest, AccessResponse
from app.core.auth.auth import get_authenticated_user
from app.core.authz.authorization import Authorization
from app.users.schema import User

router = APIRouter(prefix="/authz", tags=["authz"])


@router.post(
    "/access/check",
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
    request: AccessRequest, user: User = Depends(get_authenticated_user)
) -> AccessResponse:
    """Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.
    """
    authorizer = Authorization()

    domain = "*" if request.domain is None else request.domain
    object_ = "*" if request.object_id is None else str(request.object_id)
    access = authorizer.has_access(
        subject=str(user.id),
        domain=domain,
        object_=object_,
        action=request.action,
    )
    return AccessResponse(access=access)
