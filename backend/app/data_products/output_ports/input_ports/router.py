from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.abstract_data_product.input_ports.enums import InputPortStatus
from app.abstract_data_product.service import AbstractDataProductService
from app.abstract_data_product.type import AbstractDataProductType
from app.core.auth.auth import get_authenticated_user
from app.core.authz import (
    Action,
    Authorization,
    OutputPortResolver,
)
from app.data_products.output_ports.input_ports.schema_request import (
    ApproveOutputPortAsInputPortRequest,
    DenyOutputPortAsInputPortRequest,
    GrantOutputPortAccessRequest,
    RemoveOutputPortAsInputPortRequest,
    RevokeOutputPortAsInputPortRequest,
)
from app.data_products.output_ports.input_ports.schema_response import (
    GetInputPortsForOutputPortResponse,
)
from app.data_products.output_ports.input_ports.service import InputPortService
from app.database.deps import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter(
    tags=["Data Products - Output ports - Input ports"],
    prefix="/v2/data_products/{data_product_id}/output_ports/{output_port_id}/input_ports",
)


@router.post(
    "/grant",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                OutputPortResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def grant_output_port_access(
    data_product_id: UUID,
    output_port_id: UUID,
    body: GrantOutputPortAccessRequest,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    input_port = AbstractDataProductService(db).grant_output_port_access(
        consumer_id=body.consuming_abstract_data_product_id,
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        justification=body.justification,
        access_mode_id=body.access_mode_id,
        actor=authenticated_user,
    )

    consumer_type = (
        input_port.consuming_abstract_data_product.abstract_data_product_type
    )
    target_type = (
        EventReferenceEntity.EXPLORATION
        if consumer_type == AbstractDataProductType.EXPLORATION
        else EventReferenceEntity.DATA_PRODUCT
    )
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_APPROVED,
            subject_id=output_port_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=input_port.consuming_abstract_data_product_id,
            target_type=target_type,
            actor_id=authenticated_user.id,
        ),
    )
    notification_service = NotificationService(db)
    match consumer_type:
        case AbstractDataProductType.DATA_PRODUCT:
            notification_service.create_data_product_notifications(
                data_product_id=input_port.consuming_abstract_data_product_id,
                event_id=event_id,
            )
        case AbstractDataProductType.EXPLORATION:
            notification_service.create_exploration_notifications(
                exploration_id=input_port.consuming_abstract_data_product_id,
                event_id=event_id,
            )


@router.get(
    "/",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.HIDDEN__OUTPUT_PORT__READ,
                OutputPortResolver,
                object_id="output_port_id",
            )
        )
    ],
)
def get_input_ports_for_output_port(
    data_product_id: UUID,
    output_port_id: UUID,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> GetInputPortsForOutputPortResponse:
    return GetInputPortsForOutputPortResponse(
        input_ports=InputPortService(db).get_consuming_data_products(
            authenticated_user,
            output_port_id,
            data_product_id,
        )
    )


@router.post(
    "/approve",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                OutputPortResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def approve_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    body: ApproveOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    approved_input_port = InputPortService(db).approve_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=body.consuming_data_product_id,
        actor=authenticated_user,
        decision_note=body.decision_note,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_APPROVED,
            subject_id=approved_input_port.output_port_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=approved_input_port.consuming_abstract_data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=approved_input_port.output_port_id,
        event_id=event_id,
        extra_receiver_ids=[approved_input_port.requested_by_id],
    )


@router.post(
    "/deny",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                OutputPortResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def deny_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    body: DenyOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    input_port = InputPortService(db).deny_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=body.consuming_data_product_id,
        actor=authenticated_user,
        decision_note=body.decision_note,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_DENIED,
            subject_id=input_port.output_port_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=input_port.consuming_abstract_data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=input_port.output_port_id,
        event_id=event_id,
        extra_receiver_ids=[input_port.requested_by_id],
    )


@router.post(
    "/revoke",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
                OutputPortResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def revoke_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    body: RevokeOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    input_port = InputPortService(db).revoke_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=body.consuming_data_product_id,
        actor=authenticated_user,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_REVOKED,
            subject_id=input_port.output_port_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=input_port.consuming_abstract_data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=input_port.output_port_id,
        event_id=event_id,
        extra_receiver_ids=[input_port.latest_request.requested_by_id],
    )


@router.post(
    "/remove",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__REVOKE_DATAPRODUCT_ACCESS,
                OutputPortResolver,
                object_id="output_port_id",
            )
        ),
    ],
)
def remove_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    body: RemoveOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session, scope="function"),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    input_port = InputPortService(db).remove_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=body.consuming_data_product_id,
    )
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_REMOVED,
            subject_id=input_port.output_port_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=input_port.consuming_abstract_data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    if input_port.status == InputPortStatus.APPROVED:
        NotificationService(db).create_dataset_notifications(
            dataset_id=input_port.output_port_id,
            event_id=event_id,
            extra_receiver_ids=[input_port.latest_request.requested_by_id],
        )
