from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
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
from app.roles.service import ADMIN_UUID
from app.users.schema import User

router = APIRouter(prefix="/global")


@router.get("")
def list_assignments(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[RoleAssignmentResponse]:
    return RoleAssignmentService(db=db, user=user).list_assignments(user_id=user_id)


@router.post("")
def create_assignment(
    request: CreateRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    if (role_id := request.role_id) == "admin":
        role_id = ADMIN_UUID
    return RoleAssignmentService(db=db, user=user).create_assignment(
        RoleAssignmentRequest(user_id=request.user_id, role_id=role_id)
    )


@router.delete("/{id}")
def delete_assignment(
    id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> None:
    assignment = RoleAssignmentService(db=db, user=user).delete_assignment(id)

    if assignment.decision is DecisionStatus.APPROVED:
        background_tasks.add_task(GlobalAuthAssignment(assignment).remove)
    return None


@router.patch("/{id}/decide")
def decide_assignment(
    id: UUID,
    request: DecideRoleAssignment,
    background_tasks: BackgroundTasks,
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
        background_tasks.add_task(GlobalAuthAssignment(assignment).add)

    return assignment


@router.patch("/{id}/role")
def modify_assigned_role(
    id: UUID,
    request: ModifyRoleAssignment,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    service = RoleAssignmentService(db=db, user=user)
    original = service.get_assignment(id)

    if (role_id := request.role_id) == "admin":
        role_id = ADMIN_UUID
    assignment = service.update_assignment(UpdateRoleAssignment(id=id, role_id=role_id))

    if assignment.decision is DecisionStatus.APPROVED:
        background_tasks.add_task(
            GlobalAuthAssignment(assignment, previous=original).swap
        )

    return assignment
