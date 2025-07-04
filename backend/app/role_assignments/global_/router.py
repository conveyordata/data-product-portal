from typing import Literal, Optional, Sequence, Union, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import EmptyResolver
from app.database.database import get_db_session
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.global_.auth import GlobalAuthAssignment
from app.role_assignments.global_.schema import (
    CreateRoleAssignment,
    DecideRoleAssignment,
    ModifyRoleAssignment,
    RoleAssignmentRequest,
    RoleAssignmentResponse,
    UpdateRoleAssignment,
)
from app.role_assignments.global_.service import RoleAssignmentService
from app.roles import ADMIN_UUID
from app.users.schema import User

router = APIRouter(prefix="/global")


@router.get("")
def list_assignments(
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    db: Session = Depends(get_db_session),
) -> Sequence[RoleAssignmentResponse]:
    return RoleAssignmentService(db).list_assignments(user_id=user_id, role_id=role_id)


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
)
def create_assignment(
    request: CreateRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    role_id = _resolve_role_id(request.role_id)
    return RoleAssignmentService(db).create_assignment(
        RoleAssignmentRequest(user_id=request.user_id, role_id=role_id), actor=user
    )


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__DELETE_USER, resolver=EmptyResolver)
        )
    ],
)
def delete_assignment(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    assignment = RoleAssignmentService(db).delete_assignment(id)

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment).remove()
    return None


@router.patch(
    "/{id}/decide",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
)
def decide_assignment(
    id: UUID,
    request: DecideRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    service = RoleAssignmentService(db)
    original = service.get_assignment(id)

    if original.decision not in (DecisionStatus.PENDING, request.decision):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This assignment was already decided",
        )

    assignment = service.update_assignment(
        UpdateRoleAssignment(id=id, decision=request.decision), actor=user
    )

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment).add()

    return assignment


@router.patch(
    "/{id}/role",
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_USER, resolver=EmptyResolver)
        )
    ],
)
def modify_assigned_role(
    id: UUID,
    request: ModifyRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    service = RoleAssignmentService(db)
    original_role = service.get_assignment(id).role_id

    role_id = _resolve_role_id(request.role_id)
    assignment = service.update_assignment(
        UpdateRoleAssignment(id=id, role_id=role_id), actor=user
    )

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment, previous_role_id=original_role).swap()

    return assignment


def _resolve_role_id(role_id: Union[UUID, Literal["admin"]]) -> UUID:
    if role_id == "admin":
        return ADMIN_UUID
    return cast(UUID, role_id)
