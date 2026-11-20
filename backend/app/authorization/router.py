from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic.json_schema import SkipJsonSchema

from app.authorization.role_assignments.global_.service import RoleAssignmentService
from app.authorization.schema_response import AccessResponse, IsAdminResponse
from app.authorization.service import AuthorizationService
from app.core.auth.auth import AuthenticatedUser
from app.core.authz import Action
from app.database.deps import DbSession

router = APIRouter(tags=["Authorization"], prefix="/v2/authz")


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
    user: AuthenticatedUser,
    db: DbSession,
    resource: Annotated[UUID | SkipJsonSchema[None], Query()] = None,
    domain: Annotated[UUID | SkipJsonSchema[None], Query()] = None,
) -> AccessResponse:
    """Allows the requesting user to check whether an access check will fail or succeed.
    Useful to conditionally disable parts of the UI that are known to be inaccessible.
    """
    allowed = AuthorizationService(db).check_access(
        user_id=user.id, action=action, resource=resource, domain=domain
    )
    return AccessResponse(allowed=allowed)


@router.get(
    "/admin",
)
def is_admin(
    db: DbSession,
    user: AuthenticatedUser,
) -> IsAdminResponse:
    return IsAdminResponse(
        is_admin=RoleAssignmentService(db).is_admin(user.id),
        time=user.admin_expiry.isoformat() if user.admin_expiry else None,
    )
