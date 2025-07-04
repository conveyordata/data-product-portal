from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import (
    DataProductResolver,
    DataProductRoleAssignmentResolver,
    EmptyResolver,
)
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.notifications.service import NotificationService
from app.role_assignments.data_product import email
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
from app.users.schema import User

router = APIRouter(prefix="/data_product")


@router.get("")
def list_assignments(
    data_product_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    decision: Optional[DecisionStatus] = None,
    db: Session = Depends(get_db_session),
) -> Sequence[RoleAssignmentResponse]:
    return RoleAssignmentService(db).list_assignments(
        data_product_id=data_product_id,
        user_id=user_id,
        role_id=role_id,
        decision=decision,
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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    service = RoleAssignmentService(db=db)
    role_assignment = service.create_assignment(id, request, actor=user)

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED,
            subject_id=role_assignment.data_product_id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=role_assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=user.id,
        )
    )

    approvers: Sequence[User] = ()
    if not (is_admin := Authorization().has_admin_role(user_id=str(user.id))):
        approvers = service.users_with_authz_action(
            data_product_id=role_assignment.data_product_id,
            action=Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
        )

    if is_admin or user.id in (approver.id for approver in approvers):
        service.update_assignment(
            UpdateRoleAssignment(
                id=role_assignment.id,
                role_id=role_assignment.role_id,
                decision=DecisionStatus.APPROVED,
            ),
            actor=user,
        )
    else:
        background_tasks.add_task(
            email.send_role_assignment_request_email,
            role_assignment,
            approvers,
        )

    return role_assignment


@router.post(
    "/request/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__REQUEST_DATAPRODUCT_ACCESS, resolver=EmptyResolver
            )
        )
    ],
)
def request_assignment(
    id: UUID,
    request: CreateRoleAssignment,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponse:
    service = RoleAssignmentService(db=db)
    role_assignment = service.create_assignment(id, request, actor=user)

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REQUESTED,
            subject_id=role_assignment.data_product_id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=role_assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=user.id,
        )
    )

    approvers = service.users_with_authz_action(
        data_product_id=role_assignment.data_product_id,
        action=Action.DATA_PRODUCT__APPROVE_USER_REQUEST,
    )
    background_tasks.add_task(
        email.send_role_assignment_request_email,
        role_assignment,
        approvers,
    )
    return role_assignment


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
    assignment = RoleAssignmentService(db=db).delete_assignment(id)

    if assignment.decision is DecisionStatus.APPROVED:
        DataProductAuthAssignment(assignment).remove()

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_REMOVED,
            subject_id=assignment.data_product_id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=assignment.data_product_id,
        event_id=event_id,
        extra_receiver_ids=(
            [receiver] if (receiver := assignment.requested_by_id) is not None else []
        ),
    )


@router.patch(
    "/{id}",
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
    service = RoleAssignmentService(db)
    original_role = service.get_assignment(id).role_id

    assignment = service.update_assignment(
        UpdateRoleAssignment(id=id, role_id=request.role_id), actor=user
    )
    if assignment.decision is DecisionStatus.APPROVED:
        DataProductAuthAssignment(assignment, previous_role_id=original_role).swap()

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_UPDATED,
            subject_id=assignment.data_product_id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=assignment.data_product_id,
        event_id=event_id,
        extra_receiver_ids=(
            [requester] if (requester := assignment.requested_by_id) is not None else []
        ),
    )

    return assignment


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
    service = RoleAssignmentService(db)
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

    assignment = service.update_assignment(
        UpdateRoleAssignment(id=id, decision=request.decision), actor=user
    )
    if assignment.decision is DecisionStatus.APPROVED:
        DataProductAuthAssignment(assignment).add()

    event_id = EventService(db).create_event(
        CreateEvent(
            name=(
                EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_APPROVED
                if assignment.decision == DecisionStatus.APPROVED
                else EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_DENIED
            ),
            subject_id=assignment.data_product_id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=assignment.data_product_id,
        event_id=event_id,
        extra_receiver_ids=(
            [requester] if (requester := assignment.requested_by_id) is not None else []
        ),
    )

    return assignment
