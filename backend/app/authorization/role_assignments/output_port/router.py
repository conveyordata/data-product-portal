from typing import Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.auth import DatasetAuthAssignment
from app.authorization.role_assignments.output_port.schema import (
    CreateOutputPortRoleAssignment,
    CreateOutputPortRoleAssignmentOld,
    DecideOutputPortRoleAssignment,
    DeleteOutputPortRoleAssignmentResponse,
    ListOutputPortRoleAssignmentsResponse,
    ModifyOutputPortRoleAssignment,
    OutputPortRoleAssignmentResponse,
    RequestOutputPortRoleAssignment,
    RoleAssignmentOld,
    RoleAssignmentResponseOld,
    UpdateOutputPortRoleAssignment,
)
from app.authorization.role_assignments.output_port.service import RoleAssignmentService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization
from app.core.authz.resolvers import (
    DatasetResolver,
    DatasetRoleAssignmentResolver,
    EmptyResolver,
)
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter()


@router.delete(
    "/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__DELETE_USER,
                resolver=DatasetRoleAssignmentResolver,
            )
        )
    ],
)
def delete_output_port_role_assignment(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> DeleteOutputPortRoleAssignmentResponse:
    assignment = RoleAssignmentService(db).delete_assignment(id)
    if assignment.decision is DecisionStatus.APPROVED:
        DatasetAuthAssignment(assignment).remove()

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_ROLE_ASSIGNMENT_REMOVED,
            subject_id=assignment.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=assignment.dataset_id,
        event_id=event_id,
        extra_receiver_ids=(
            [requester] if (requester := assignment.requested_by_id) is not None else []
        ),
    )
    return DeleteOutputPortRoleAssignmentResponse(
        id=assignment.id,
        output_port_id=assignment.dataset_id,
    )


_router = router
router = APIRouter()

old_route = "/role_assignments/dataset"
route = "/v2/authz/role_assignments/output_port"
router.include_router(_router, prefix=old_route, deprecated=True)
router.include_router(_router, prefix=route)


@router.get(old_route, deprecated=True)
def list_assignments_old(
    dataset_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    decision: Optional[DecisionStatus] = None,
    db: Session = Depends(get_db_session),
) -> Sequence[RoleAssignmentResponseOld]:
    return RoleAssignmentService(db).list_assignments(
        dataset_id=dataset_id, user_id=user_id, role_id=role_id, decision=decision
    )


def convert_to_role_assignment(
    assignment: RoleAssignmentResponseOld,
) -> OutputPortRoleAssignmentResponse:
    return OutputPortRoleAssignmentResponse(
        id=assignment.id,
        output_port=assignment.dataset,
        user=assignment.user,
        role=assignment.role,
        decision=assignment.decision,
        requested_on=assignment.requested_on,
        requested_by=assignment.requested_by,
        decided_on=assignment.decided_on,
        decided_by=assignment.decided_by,
    )


@router.get(route)
def list_output_port_role_assignments(
    output_port_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    decision: Optional[DecisionStatus] = None,
    db: Session = Depends(get_db_session),
) -> ListOutputPortRoleAssignmentsResponse:
    return ListOutputPortRoleAssignmentsResponse(
        role_assignments=[
            convert_to_role_assignment(x)
            for x in RoleAssignmentService(db).list_assignments(
                dataset_id=output_port_id,
                user_id=user_id,
                role_id=role_id,
                decision=decision,
            )
        ]
    )


@router.post(
    f"{old_route}/request/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS, resolver=EmptyResolver
            )
        )
    ],
    deprecated=True,
)
def request_assignment_old(
    id: UUID,
    request: CreateOutputPortRoleAssignmentOld,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> RoleAssignmentOld:
    assignment = RoleAssignmentService(db).create_assignment(
        dataset_id=id,
        role_id=request.role_id,
        user_id=request.user_id,
        actor=authenticated_user,
    )

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_ROLE_ASSIGNMENT_REQUESTED,
            subject_id=assignment.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=authenticated_user.id,
        )
    )

    return assignment


@router.post(
    f"{route}/request",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.GLOBAL__REQUEST_OUTPUT_PORT_ACCESS, resolver=EmptyResolver
            )
        )
    ],
)
def request_output_port_role_assignment(
    request: RequestOutputPortRoleAssignment,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> OutputPortRoleAssignmentResponse:
    return convert_to_role_assignment(
        request_assignment_old(
            request.output_port_id,
            CreateOutputPortRoleAssignmentOld(
                user_id=request.user_id, role_id=request.role_id
            ),
            db,
            authenticated_user,
        )
    )


@router.post(
    f"{old_route}/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__CREATE_USER, resolver=DatasetResolver
            )
        )
    ],
    deprecated=True,
)
def create_assignment_old(
    id: UUID,
    request: CreateOutputPortRoleAssignmentOld,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponseOld:
    service = RoleAssignmentService(db)
    role_assignment = service.create_assignment(
        dataset_id=id,
        user_id=request.user_id,
        role_id=request.role_id,
        actor=authenticated_user,
    )

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_ROLE_ASSIGNMENT_CREATED,
            subject_id=role_assignment.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=role_assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=authenticated_user.id,
        )
    )

    approvers: Sequence[User] = ()
    if not (
        is_admin := Authorization().has_admin_role(user_id=str(authenticated_user.id))
    ):
        approvers = service.users_with_authz_action(
            dataset_id=role_assignment.dataset_id,
            action=Action.OUTPUT_PORT__APPROVE_USER_REQUEST,
        )

    if is_admin or authenticated_user.id in (approver.id for approver in approvers):
        assignment = service.update_assignment(
            UpdateOutputPortRoleAssignment(
                id=role_assignment.id,
                role_id=role_assignment.role_id,
                decision=DecisionStatus.APPROVED,
            ),
            actor=authenticated_user,
        )
        DatasetAuthAssignment(assignment).add()

    return role_assignment


@router.post(
    f"{route}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__CREATE_USER,
                resolver=DatasetResolver,
                object_id="output_port_id",
            )
        )
    ],
)
def create_output_port_role_assignment(
    request: CreateOutputPortRoleAssignment,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> OutputPortRoleAssignmentResponse:
    return convert_to_role_assignment(
        create_assignment_old(
            request.output_port_id,
            CreateOutputPortRoleAssignmentOld(
                user_id=request.user_id, role_id=request.role_id
            ),
            db,
            authenticated_user,
        )
    )


@router.patch(
    f"{old_route}/{{id}}/decide",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_USER_REQUEST,
                resolver=DatasetRoleAssignmentResolver,
            )
        )
    ],
    deprecated=True,
)
def decide_assignment_old(
    id: UUID,
    request: DecideOutputPortRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponseOld:
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
        UpdateOutputPortRoleAssignment(id=id, decision=request.decision), actor=user
    )
    if assignment.decision is DecisionStatus.APPROVED:
        DatasetAuthAssignment(assignment).add()

    event_id = EventService(db).create_event(
        CreateEvent(
            name=(
                EventType.DATASET_ROLE_ASSIGNMENT_APPROVED
                if assignment.decision == DecisionStatus.APPROVED
                else EventType.DATASET_ROLE_ASSIGNMENT_DENIED
            ),
            subject_id=assignment.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=assignment.dataset_id,
        event_id=event_id,
        extra_receiver_ids=(
            [assignment.requested_by_id]
            if assignment.requested_by_id is not None
            else []
        ),
    )

    return assignment


@router.post(
    f"{route}/{{id}}/decide",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_USER_REQUEST,
                resolver=DatasetRoleAssignmentResolver,
            )
        )
    ],
)
def decide_output_port_role_assignment(
    id: UUID,
    request: DecideOutputPortRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> OutputPortRoleAssignmentResponse:
    return convert_to_role_assignment(decide_assignment_old(id, request, db, user))


@router.patch(
    f"{old_route}/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_USER,
                resolver=DatasetRoleAssignmentResolver,
            )
        )
    ],
    deprecated=True,
)
def modify_assigned_role_old(
    id: UUID,
    request: ModifyOutputPortRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> RoleAssignmentResponseOld:
    service = RoleAssignmentService(db)
    original_role = service.get_assignment(id).role_id

    assignment = service.update_assignment(
        UpdateOutputPortRoleAssignment(id=id, role_id=request.role_id), actor=user
    )
    if assignment.decision is DecisionStatus.APPROVED:
        DatasetAuthAssignment(assignment, previous_role_id=original_role).swap()

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_ROLE_ASSIGNMENT_UPDATED,
            subject_id=assignment.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=assignment.user_id,
            target_type=EventReferenceEntity.USER,
            actor_id=user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=assignment.dataset_id,
        event_id=event_id,
        extra_receiver_ids=(
            [requester] if (requester := assignment.requested_by_id) is not None else []
        ),
    )

    return assignment


@router.put(
    f"{route}/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_USER,
                resolver=DatasetRoleAssignmentResolver,
            )
        )
    ],
)
def modify_output_port_role_assignment(
    id: UUID,
    request: ModifyOutputPortRoleAssignment,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> OutputPortRoleAssignmentResponse:
    return convert_to_role_assignment(modify_assigned_role_old(id, request, db, user))
