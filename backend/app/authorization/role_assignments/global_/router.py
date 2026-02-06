from typing import Literal, Optional, Sequence, Union, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.global_.auth import GlobalAuthAssignment
from app.authorization.role_assignments.global_.schema import (
    BecomeAdmin,
    CreateGlobalRoleAssignment,
    DecideGlobalRoleAssignment,
    DeleteGlobalRoleAssignmentResponse,
    GlobalRoleAssignmentResponse,
    ListGlobalRoleAssignmentsResponse,
    ModifyGlobalRoleAssignment,
    RoleAssignmentRequest,
    UpdateGlobalRoleAssignment,
)
from app.authorization.role_assignments.global_.service import RoleAssignmentService
from app.authorization.roles import ADMIN_UUID
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session
from app.users.model import ensure_user_exists
from app.users.schema import User

router = APIRouter()


@router.post(
    "/become_admin",
)
def become_admin(
    request: BecomeAdmin,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
):
    user = ensure_user_exists(user.id, db)
    if not user.can_become_admin:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="User is not allowed to elevate to admin",
        )
    user.admin_expiry = request.expiry
    authorizer = Authorization()
    authorizer.assign_admin_role(user_id=str(user.id))


@router.post(
    "/revoke_admin",
)
def revoke_admin(
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
):
    user = ensure_user_exists(user.id, db)
    authorizer = Authorization()
    authorizer.revoke_admin_role(user_id=user.id)


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
)
def create_global_role_assignment(
    request: CreateGlobalRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> GlobalRoleAssignmentResponse:
    role_id = _resolve_role_id(request.role_id)
    return RoleAssignmentService(db).create_assignment(
        RoleAssignmentRequest(user_id=request.user_id, role_id=role_id),
        actor=user,
    )


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__DELETE_USER, resolver=EmptyResolver)
        )
    ],
)
def delete_global_role_assignment(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> DeleteGlobalRoleAssignmentResponse:
    assignment = RoleAssignmentService(db).delete_assignment(id)

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment).remove()
    return DeleteGlobalRoleAssignmentResponse(id=assignment.id)


def _resolve_role_id(role_id: Union[UUID, Literal["admin"]]) -> UUID:
    if role_id == "admin":
        return ADMIN_UUID
    return cast("UUID", role_id)


_router = router
router = APIRouter()

old_route = "/role_assignments/global"
route = "/v2/authz/role_assignments/global"
router.include_router(_router, prefix=old_route, deprecated=True)
router.include_router(_router, prefix=route)


@router.get(old_route, deprecated=True)
def list_assignments_old(
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    db: Session = Depends(get_db_session),
) -> Sequence[GlobalRoleAssignmentResponse]:
    return list_global_role_assignments(
        user_id=user_id, role_id=role_id, db=db
    ).role_assignments


@router.get(route)
def list_global_role_assignments(
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    db: Session = Depends(get_db_session),
) -> ListGlobalRoleAssignmentsResponse:
    return ListGlobalRoleAssignmentsResponse(
        role_assignments=RoleAssignmentService(db).list_assignments(
            user_id=user_id, role_id=role_id
        )
    )


@router.patch(
    f"{old_route}/{{id}}/decide",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
    deprecated=True,
)
def decide_assignment_old(
    id: UUID,
    request: DecideGlobalRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> GlobalRoleAssignmentResponse:
    return decide_global_role_assignment(id, request, db, user)


@router.post(
    f"{route}/{{id}}/decide",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
)
def decide_global_role_assignment(
    id: UUID,
    request: DecideGlobalRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> GlobalRoleAssignmentResponse:
    service = RoleAssignmentService(db)
    original = service.get_assignment(id)

    if original.decision not in (DecisionStatus.PENDING, request.decision):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This assignment was already decided",
        )

    assignment = service.update_assignment(
        UpdateGlobalRoleAssignment(id=id, decision=request.decision), actor=user
    )

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment).add()

    return assignment


@router.patch(
    f"{old_route}/{{id}}/role",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
    deprecated=True,
)
def modify_assigned_role_old(
    id: UUID,
    request: ModifyGlobalRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> GlobalRoleAssignmentResponse:
    return modify_global_role_assignment(id, request, db, user)


@router.put(
    f"{route}/{{id}}/role",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
)
def modify_global_role_assignment(
    id: UUID,
    request: ModifyGlobalRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> GlobalRoleAssignmentResponse:
    service = RoleAssignmentService(db)
    original_role = service.get_assignment(id).role_id

    role_id = _resolve_role_id(request.role_id)
    assignment = service.update_assignment(
        UpdateGlobalRoleAssignment(id=id, role_id=role_id), actor=user
    )

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment, previous_role_id=original_role).swap()

    return assignment
