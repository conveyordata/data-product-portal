from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.core.auth.auth import get_authenticated_user
from app.core.authz import (
    Action,
    Authorization,
    DataProductDatasetAssociationResolver,
    DatasetResolver,
)
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products.output_ports.input_ports.schema_request import (
    ApproveOutputPortAsInputPortRequest,
    DenyOutputPortAsInputPortRequest,
    RemoveOutputPortAsInputPortRequest,
)
from app.data_products.output_ports.input_ports.service import DataProductDatasetService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.pending_actions.schema import DataProductDatasetPendingAction
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter(tags=["Data Products - Output ports - Input ports"])
old_route = "/data_product_dataset_links"
route = "/v2/data_products/{data_product_id}/output_ports/{output_port_id}/input_ports"


@router.post(
    f"{old_route}/approve/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
    deprecated=True,
)
def approve_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).get_link_by_id(id)
    approve_output_port_as_input_port(
        data_product_id=data_product_link.dataset.data_product_id,
        output_port_id=data_product_link.dataset_id,
        request=ApproveOutputPortAsInputPortRequest(
            consuming_data_product_id=data_product_link.data_product_id
        ),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/approve",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DatasetResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def approve_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    request: ApproveOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> ApproveOutputPortAsInputPortRequest:
    data_product_link = DataProductDatasetService(db).approve_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=request.consuming_data_product_id,
        actor=authenticated_user,
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
    return request


@router.post(
    f"{old_route}/deny/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
    deprecated=True,
)
def deny_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).get_link_by_id(
        id,
    )
    deny_output_port_as_input_port(
        data_product_id=data_product_link.dataset.data_product_id,
        output_port_id=data_product_link.dataset_id,
        request=DenyOutputPortAsInputPortRequest(
            consuming_data_product_id=data_product_link.data_product_id
        ),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/deny",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DatasetResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def deny_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    request: DenyOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).deny_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=request.consuming_data_product_id,
        actor=authenticated_user,
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
    f"{old_route}/remove/{{id}}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
                DataProductDatasetAssociationResolver,
            )
        ),
    ],
    deprecated=True,
)
def remove_data_product_link(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).get_link_by_id(id)
    remove_output_port_as_input_port(
        data_product_id=data_product_link.dataset.data_product_id,
        output_port_id=data_product_link.dataset_id,
        request=RemoveOutputPortAsInputPortRequest(
            consuming_data_product_id=data_product_link.data_product_id
        ),
        db=db,
        authenticated_user=authenticated_user,
    )


@router.post(
    f"{route}/remove",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
                DatasetResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def remove_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    request: RemoveOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).remove_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=request.consuming_data_product_id,
    )
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


@router.get(f"{old_route}/actions", deprecated=True)
def get_user_pending_actions(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[DataProductDatasetPendingAction]:
    return DataProductDatasetService(db).get_user_pending_actions(authenticated_user)
