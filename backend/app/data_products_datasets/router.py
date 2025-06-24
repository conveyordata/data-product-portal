from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataProductDatasetAssociationResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products_datasets.service import DataProductDatasetService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.notifications.service import NotificationService
from app.pending_actions.schema import DataProductDatasetPendingAction
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User

router = APIRouter(
    prefix="/data_product_dataset_links", tags=["data_product_dataset_links"]
)


@router.post(
    "/approve/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
)
def approve_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).approve_data_product_link(
        id, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_APPROVED,
            subject_id=data_product_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=data_product_link.data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=data_product_link.dataset_id,
        event_id=event_id,
        extra_receiver_ids=[data_product_link.requested_by_id],
    )
    RefreshInfrastructureLambda().trigger()


@router.post(
    "/deny/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
)
def deny_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).deny_data_product_link(
        id, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_DENIED,
            subject_id=data_product_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=data_product_link.data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=data_product_link.dataset_id,
        event_id=event_id,
        extra_receiver_ids=[data_product_link.requested_by_id],
    )


@router.post(
    "/remove/{id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATASET__REVOKE_DATAPRODUCT_ACCESS,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
)
def remove_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).remove_data_product_link(id)

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_REMOVED,
            subject_id=data_product_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=data_product_link.data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    if data_product_link.status == DecisionStatus.APPROVED:
        NotificationService(db).create_dataset_notifications(
            dataset_id=data_product_link.dataset_id,
            event_id=event_id,
            extra_receiver_ids=[data_product_link.requested_by_id],
        )
    RefreshInfrastructureLambda().trigger()


@router.get("/actions")
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[DataProductDatasetPendingAction]:
    return DataProductDatasetService(db).get_user_pending_actions(authenticated_user)
