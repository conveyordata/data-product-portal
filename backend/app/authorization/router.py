from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy import select

from app.authorization.role_assignments.global_.service import RoleAssignmentService
from app.authorization.schema_response import AccessResponse, IsAdminResponse
from app.core.auth.auth import AuthenticatedUser
from app.core.authz import Action, Authorization
from app.data_products.output_ports.model import OutputPort
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
    sub = str(user.id)
    dom = "*" if domain is None else str(domain)
    obj = "*" if resource is None else str(resource)
    parent = "*"
    if resource is not None and action.name.startswith("OUTPUT_PORT__"):
        data_product_id = db.scalar(
            select(OutputPort.data_product_id).where(OutputPort.id == resource)
        )
        if data_product_id is not None:
            parent = str(data_product_id)

    authorizer = Authorization()
    result = authorizer.has_access(sub=sub, dom=dom, obj=obj, parent=parent, act=action)
    return AccessResponse(allowed=result)


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
