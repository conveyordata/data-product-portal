from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.database.database import get_db_session
from app.role_assignments.data_product.schema import (
    CreateRoleAssignment,
    DecideRoleAssignment,
    ModifyRoleAssignment,
    RoleAssignment,
)
from app.role_assignments.data_product.service import RoleAssignmentService
from app.users.model import User

router = APIRouter(prefix="/data_product")


@router.get("/")
def list_assignments(
    data_product_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[RoleAssignment]:
    return RoleAssignmentService(db=db, user=user).list_assignments(
        data_product_id, user_id
    )


@router.post("/")
def create_assignment(
    request: CreateRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignment:
    return RoleAssignmentService(db=db, user=user).create_assignments(request)


@router.delete("/{id}")
def delete_assignment(
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> None:
    return None


@router.patch("/{id}/decide")
def decide_assignment(
    id: UUID,
    request: DecideRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignment:
    return None


@router.patch("/{id}/role")
def change_assignment_role(
    id: UUID,
    request: ModifyRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignment:
    return None
