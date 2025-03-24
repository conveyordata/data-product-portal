from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_db_session
from app.role_assignments import tasks
from app.role_assignments.data_product.schema import (
    CreateRoleAssignment,
    DecideRoleAssignment,
    ModifyRoleAssignment,
    RoleAssignmentResponse,
    UpdateRoleAssignment,
)
from app.role_assignments.data_product.service import RoleAssignmentService
from app.role_assignments.enums import DecisionStatus
from app.role_assignments.tasks import AuthAssignment
from app.users.model import User

router = APIRouter(prefix="/data_product")


@router.get("/")
def list_assignments(
    data_product_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[RoleAssignmentResponse]:
    return RoleAssignmentService(db=db, user=user).list_assignments(
        data_product_id, user_id
    )


@router.post("/")
def create_assignment(
    request: CreateRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    return RoleAssignmentService(db=db, user=user).create_assignment(request)


@router.delete("/{id}")
def delete_assignment(
    id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> None:
    assignment = RoleAssignmentService(db=db, user=user).delete_assignment(id)

    if assignment.decision is DecisionStatus.APPROVED:
        background_tasks.add_task(
            tasks.remove_assignment, AuthAssignment.from_data_product(assignment)
        )
    return None


@router.patch("/{id}/decide")
def decide_assignment(
    id: UUID,
    request: DecideRoleAssignment,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    assignment = RoleAssignmentService(db=db, user=user).update_assignment(
        UpdateRoleAssignment(id=id, decision=request.decision)
    )

    if assignment.decision is DecisionStatus.APPROVED:
        background_tasks.add_task(
            tasks.add_assignment, AuthAssignment.from_data_product(assignment)
        )

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
    original_role = service.get_assignment(id).role.id

    assignment = service.update_assignment(
        UpdateRoleAssignment(id=id, role_id=request.role_id)
    )

    if assignment.decision is DecisionStatus.APPROVED:
        background_tasks.add_task(
            tasks.swap_assignment,
            AuthAssignment.from_data_product(assignment).with_previous(original_role),
        )

    return assignment
