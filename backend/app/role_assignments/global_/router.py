from typing import Literal, Optional, Sequence, Union, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz.authorization import Authorization
from app.core.authz.authorization import AuthorizationAction as Action
from app.core.authz.resolvers import DataProductResolver
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
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[RoleAssignmentResponse]:
    return RoleAssignmentService(db=db, user=user).list_assignments(user_id=user_id)


@router.post(
    "",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__ASSIGN_ROLE, resolver=DataProductResolver
            )
        )
    ],
)
def create_assignment(
    request: CreateRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    role_id = _resolve_role_id(request.role_id)
    return RoleAssignmentService(db=db, user=user).create_assignment(
        RoleAssignmentRequest(user_id=request.user_id, role_id=role_id)
    )


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__DELETE_ROLE_ASSIGNMENT, resolver=DataProductResolver
            )
        )
    ],
)
def delete_assignment(
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> None:
    assignment = RoleAssignmentService(db=db, user=user).delete_assignment(id)

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment).remove()
    return None


@router.patch(
    "/{id}/decide",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__DECIDE_ROLE_ASSIGNMENT, resolver=DataProductResolver
            )
        )
    ],
)
def decide_assignment(
    id: UUID,
    request: DecideRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    service = RoleAssignmentService(db=db, user=user)
    original = service.get_assignment(id)

    if original.decision not in (DecisionStatus.PENDING, request.decision):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="This assignment was already decided",
        )

    assignment = service.update_assignment(
        UpdateRoleAssignment(id=id, decision=request.decision)
    )

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment).add()

    return assignment


@router.patch(
    "/{id}/role",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__UPDATE_ROLE_ASSIGNMENT, resolver=DataProductResolver
            )
        )
    ],
)
def modify_assigned_role(
    id: UUID,
    request: ModifyRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    service = RoleAssignmentService(db=db, user=user)
    original_role = service.get_assignment(id).role_id

    role_id = _resolve_role_id(request.role_id)
    assignment = service.update_assignment(UpdateRoleAssignment(id=id, role_id=role_id))

    if assignment.decision is DecisionStatus.APPROVED:
        GlobalAuthAssignment(assignment, previous_role_id=original_role).swap()

    return assignment


def _resolve_role_id(role_id: Union[UUID, Literal["admin"]]) -> UUID:
    if role_id == "admin":
        return ADMIN_UUID
    return cast(UUID, role_id)
