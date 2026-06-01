from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.abstract_data_product.schema_response import GetAbstractDataProductResponse
from app.authorization.role_assignments.enums import DecisionStatus
from app.core.auth.auth import get_authenticated_user
from app.core.authz import (
    Action,
    Authorization,
    DatasetResolver,
)
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.webhooks.events import (
    OutputPortLinkApprovedEvent,
    OutputPortLinkDeniedEvent,
)
from app.core.webhooks.v2 import _emits_event
from app.data_products.output_ports.input_ports.schema_request import (
    ApproveOutputPortAsInputPortRequest,
    DenyOutputPortAsInputPortRequest,
    RemoveOutputPortAsInputPortRequest,
)
from app.data_products.output_ports.input_ports.schema_response import (
    GetInputPortsForOutputPortResponse,
    OutputPortInputPort,
)
from app.data_products.output_ports.input_ports.service import DataProductDatasetService
from app.data_products.output_ports.schema_response import (
    GetOutputPortResponse,
)
from app.data_products.output_ports.service import OutputPortService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.service import EventService
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter(tags=["Data Products - Output ports - Input ports"])
route = "/v2/data_products/{data_product_id}/output_ports/{output_port_id}/input_ports"


@router.get(route)
def get_input_ports_for_output_port(
    data_product_id: UUID,
    output_port_id: UUID,
    db: Session = Depends(get_db_session),
) -> GetInputPortsForOutputPortResponse:
    return GetInputPortsForOutputPortResponse(
        input_ports=[
            OutputPortInputPort.model_validate(x)
            for x in OutputPortService(db).get_consuming_data_products(
                output_port_id, data_product_id
            )
        ]
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
        Depends(_emits_event(OutputPortLinkApprovedEvent)),
    ],
)
def approve_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    http_request: Request,
    body: ApproveOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).approve_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=body.consuming_data_product_id,
        actor=authenticated_user,
    )
    http_request.state.event = OutputPortLinkApprovedEvent(
        abstract_data_product=GetAbstractDataProductResponse.model_validate(
            data_product_link.consuming_abstract_data_product
        ),
        output_port=GetOutputPortResponse.model_validate(
            OutputPortService(db).get_dataset(output_port_id, data_product_id)
        ),
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_APPROVED,
            subject_id=data_product_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=data_product_link.consuming_abstract_data_product_id,
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
    f"{route}/deny",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
                DatasetResolver,
                object_id="output_port_id",
            )
        ),
        Depends(_emits_event(OutputPortLinkDeniedEvent)),
    ],
)
def deny_output_port_as_input_port(
    data_product_id: UUID,
    output_port_id: UUID,
    http_request: Request,
    body: DenyOutputPortAsInputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_link = DataProductDatasetService(db).deny_output_port_as_input_port(
        data_product_id=data_product_id,
        output_port_id=output_port_id,
        consuming_data_product_id=body.consuming_data_product_id,
        actor=authenticated_user,
    )
    http_request.state.event = OutputPortLinkDeniedEvent(
        abstract_data_product=GetAbstractDataProductResponse.model_validate(
            data_product_link.consuming_abstract_data_product
        ),
        output_port=GetOutputPortResponse.model_validate(
            OutputPortService(db).get_dataset(output_port_id, data_product_id)
        ),
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_DATASET_LINK_DENIED,
            subject_id=data_product_link.dataset_id,
            subject_type=EventReferenceEntity.DATASET,
            target_id=data_product_link.consuming_abstract_data_product_id,
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
            target_id=data_product_link.consuming_abstract_data_product_id,
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
