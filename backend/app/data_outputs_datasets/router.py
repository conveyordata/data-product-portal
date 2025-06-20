from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataOutputDatasetAssociationResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_outputs_datasets.service import DataOutputDatasetService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.notifications.service import NotificationService
from app.pending_actions.schema import DataOutputDatasetPendingAction
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User

router = APIRouter(
    prefix="/data_output_dataset_links", tags=["data_output_dataset_links"]
)


@router.post(
    "/approve/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
                DataOutputDatasetAssociationResolver,
            )
        )
    ],
)
def approve_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_link = DataOutputDatasetService(db).approve_data_output_link(
        id, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_APPROVED,
            subject_id=output_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=output_link.data_output_id,
            target_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=output_link.dataset_id,
        event_id=event_id,
        extra_receiver_ids=[output_link.requested_by_id],
    )
    RefreshInfrastructureLambda().trigger()


@router.post(
    "/deny/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
                DataOutputDatasetAssociationResolver,
            )
        )
    ],
)
def deny_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_link = DataOutputDatasetService(db).deny_data_output_link(
        id, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_DENIED,
            subject_id=output_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=output_link.data_output_id,
            target_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=output_link.dataset_id,
        event_id=event_id,
        extra_receiver_ids=[output_link.requested_by_id],
    )


@router.post(
    "/remove/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__REVOKE_DATA_OUTPUT_LINK,
                DataOutputDatasetAssociationResolver,
            )
        )
    ],
)
def remove_data_output_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_link = DataOutputDatasetService(db).remove_data_output_link(
        id, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_REMOVED,
            subject_id=output_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=output_link.data_output_id,
            target_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        ),
    )
    if output_link.status == DecisionStatus.APPROVED:
        NotificationService(db).create_dataset_notifications(
            dataset_id=output_link.dataset_id,
            event_id=event_id,
            extra_receiver_ids=[output_link.requested_by_id],
        )
    RefreshInfrastructureLambda().trigger()


@router.get("/actions")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[DataOutputDatasetPendingAction]:
    return DataOutputDatasetService(db).get_user_pending_actions(authenticated_user)
