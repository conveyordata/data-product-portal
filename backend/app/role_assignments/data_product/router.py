from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import (
    DataProductResolver,
    DataProductRoleAssignmentResolver,
)
from app.database.database import get_db_session
from app.role_assignments.data_product.auth import DataProductAuthAssignment
from app.role_assignments.data_product.schema import (
    CreateRoleAssignment,
    DecideRoleAssignment,
    ModifyRoleAssignment,
    RoleAssignmentResponse,
    UpdateRoleAssignment,
)
from app.role_assignments.data_product.service import RoleAssignmentService
from app.role_assignments.enums import DecisionStatus
from app.users.model import User

router = APIRouter(prefix="/data_product")


@router.get("")
def list_assignments(
    data_product_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    decision: Optional[DecisionStatus] = None,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[RoleAssignmentResponse]:
    return RoleAssignmentService(db=db, user=user).list_assignments(
        data_product_id=data_product_id, user_id=user_id, decision=decision
    )


@router.post(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__CREATE_USER, resolver=DataProductResolver
            )
        )
    ],
)
def create_assignment(
    id: UUID,
    request: CreateRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    return RoleAssignmentService(db=db, user=user).create_assignment(id, request)


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__DELETE_USER,
                resolver=DataProductRoleAssignmentResolver,
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
        DataProductAuthAssignment(assignment).remove()
    return None


@router.patch(
    "/{id}/decide",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
                resolver=DataProductRoleAssignmentResolver,
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

    if request.decision is DecisionStatus.APPROVED and original.role_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot approve a request that does not have a role assignment",
        )

    assignment = RoleAssignmentService(db=db, user=user).update_assignment(
        UpdateRoleAssignment(id=id, decision=request.decision)
    )

    if assignment.decision is DecisionStatus.APPROVED:
        DataProductAuthAssignment(assignment).add()

    return assignment


@router.patch(
    "/{id}/role",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_USER,
                resolver=DataProductRoleAssignmentResolver,
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

    assignment = service.update_assignment(
        UpdateRoleAssignment(id=id, role_id=request.role_id)
    )

    if assignment.decision is DecisionStatus.APPROVED:
        DataProductAuthAssignment(assignment, previous_role_id=original_role).swap()

    return assignment
