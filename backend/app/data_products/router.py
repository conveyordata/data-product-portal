from typing import Annotated, Sequence
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    status,
)
from fastapi.responses import Response
from pydantic.json_schema import SkipJsonSchema
from sqlalchemy.orm import Session

from app.abstract_data_product.schema_request import FinalizerRequest
from app.abstract_data_product.schema_response import AbstractDataProductInputPort
from app.authorization.role_assignments.data_product.auth import (
    DataProductAuthAssignment,
)
from app.authorization.role_assignments.data_product.schema import (
    UpdateDataProductRoleAssignment,
)
from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.roles.schema import Prototype, Scope
from app.authorization.roles.service import RoleService
from app.configuration.data_product_settings.service import DataProductSettingService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataProductResolver
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
    DataProductUsageUpdate,
    LinkInputPortsToDataProduct,
    RequestInputPortsForDataProductRequest,
)
from app.data_products.schema_response import (
    CreateDataProductResponse,
    GetDataProductInputPortsResponse,
    GetDataProductResponse,
    GetDataProductRolledUpTagsResponse,
    GetDataProductSettingsResponse,
    GetDataProductsResponse,
    GetDataProductsResponseItem,
    LinkInputPortsToDataProductPost,
    RenewInputPortForDataProductResponse,
    RequestInputPortsForDataProductResponse,
    UpdateDataProductResponse,
)
from app.data_products.service import DataProductService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import (
    GetEventHistoryResponse,
    GetEventHistoryResponseItemOld,
)
from app.events.service import EventService
from app.graph.graph import Graph
from app.users.notifications.service import NotificationService
from app.users.schema import User

router = APIRouter(tags=["Data Products"], prefix="/v2/data_products")


@router.post(
    "",
    responses={
        200: {
            "description": "Data Product successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_product"}
                }
            },
        },
        404: {
            "description": "Owner not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User id for owner not found"}
                }
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_DATAPRODUCT, EmptyResolver)
        ),
    ],
)
def create_data_product(
    data_product: DataProductCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateDataProductResponse:
    created_data_product = DataProductService(db).create_data_product(data_product)
    created_id = created_data_product.id
    owners = data_product.owners
    _assign_owner_role_assignments(
        created_id,
        owners=owners,
        db=db,
        actor=authenticated_user,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_CREATED,
            subject_id=created_id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=created_id,
        event_id=event_id,
        extra_receiver_ids=owners,
    )
    RefreshInfrastructureLambda().trigger()
    if data_product.input_ports is not None:
        request_input_ports_for_data_product(
            created_id,
            data_product.input_ports,
            background_tasks=background_tasks,
            authenticated_user=authenticated_user,
            db=db,
        )
    return CreateDataProductResponse(id=created_id)


def _assign_owner_role_assignments(
    data_product_id: UUID, owners: Sequence[UUID], db: Session, actor: User
) -> None:
    owner_role = RoleService(db).find_prototype(Scope.DATA_PRODUCT, Prototype.OWNER)

    assignment_service = RoleAssignmentService(db)
    for owner_id in owners:
        response = assignment_service.create_assignment(
            data_product_id,
            user_id=owner_id,
            role_id=owner_role.id,
            actor=actor,
        )
        assignment = assignment_service.update_assignment(
            UpdateDataProductRoleAssignment(
                id=response.id, decision=DecisionStatus.APPROVED
            ),
            actor=actor,
        )
        DataProductAuthAssignment(assignment).add()
        EventService(db).create_event(
            CreateEvent(
                name=EventType.DATA_PRODUCT_ROLE_ASSIGNMENT_CREATED,
                subject_id=response.data_product_id,
                subject_type=EventReferenceEntity.DATA_PRODUCT,
                target_id=response.user_id,
                target_type=EventReferenceEntity.USER,
                actor_id=actor.id,
            )
        )


@router.delete(
    "/{id}",
    responses={
        200: {"description": "Data Product deleted"},
        202: {
            "description": "Data Product marked for deletion, waiting for finalizers"
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATA_PRODUCT__DELETE, DataProductResolver)
        ),
    ],
)
def remove_data_product(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    service = DataProductService(db)
    can_delete = service.mark_for_deletion(id)
    if not can_delete:
        return Response(status_code=status.HTTP_202_ACCEPTED)
    _do_delete_data_product(id, db, authenticated_user)


def _do_delete_data_product(
    id: UUID,
    db: Session,
    authenticated_user: User,
) -> None:
    data_product = DataProductService(db).remove_data_product(id)
    Authorization().clear_assignments_for_resource(resource_id=str(id))
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_REMOVED,
            actor_id=authenticated_user.id,
            subject_id=data_product.id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            deleted_subject_identifier=data_product.name,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=data_product.id, event_id=event_id
    )


@router.post(
    "/{id}/finalizers",
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATA_PRODUCT__DELETE, DataProductResolver)
        ),
    ],
)
def add_data_product_finalizer(
    id: UUID,
    request: FinalizerRequest,
    db: Session = Depends(get_db_session),
) -> None:
    DataProductService(db).add_finalizer(id, request.finalizer)


@router.delete(
    "/{id}/finalizers/{finalizer}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATA_PRODUCT__DELETE, DataProductResolver)
        ),
    ],
)
def remove_data_product_finalizer(
    id: UUID,
    finalizer: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    should_delete = DataProductService(db).remove_finalizer(id, finalizer)
    if should_delete:
        _do_delete_data_product(id, db, authenticated_user)


@router.put(
    "/{id}",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_PROPERTIES, DataProductResolver
            )
        ),
    ],
)
def update_data_product(
    id: UUID,
    data_product: DataProductUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateDataProductResponse:
    result = DataProductService(db).update_data_product(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
    OutputPortService(db).recalculate_search_for_output_ports_of_product(id)
    return result


@router.put(
    "/{id}/about",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_PROPERTIES, DataProductResolver
            )
        ),
    ],
)
def update_data_product_about(
    id: UUID,
    data_product: DataProductAboutUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DataProductService(db).update_data_product_about(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    "/{id}/status",
    responses={
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_STATUS, DataProductResolver
            )
        ),
    ],
)
def update_data_product_status(
    id: UUID,
    data_product: DataProductStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DataProductService(db).update_data_product_status(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    "/{id}/usage",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_PROPERTIES, DataProductResolver
            )
        ),
    ],
)
def update_data_product_usage(
    id: UUID,
    usage: DataProductUsageUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DataProductService(db).update_data_product_usage(id, usage)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )


@router.get("/{id}/graph")
def get_data_product_graph_data(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    return DataProductService(db).get_graph_data(id, level)


@router.post(
    "/{id}/settings/{setting_id}",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_SETTINGS, DataProductResolver
            )
        ),
    ],
)
def set_value_for_data_product(
    id: UUID,
    setting_id: UUID,
    value: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DataProductSettingService(db).set_value_for_product(setting_id, id, value)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_SETTING_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()


_input_ports_responses = {
    400: {
        "description": "Output port not found",
        "content": {
            "application/json": {"example": {"detail": "Output port not found"}}
        },
    },
    404: {
        "description": "Data Product not found",
        "content": {
            "application/json": {"example": {"detail": "Data Product id not found"}}
        },
    },
}
_input_ports_dependencies = [
    Depends(
        Authorization.enforce(
            Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
            DataProductResolver,
        )
    ),
]


@router.post(
    "/{id}/link_input_ports",
    responses=_input_ports_responses,
    dependencies=_input_ports_dependencies,
    deprecated=True,
)
def link_input_ports_to_data_product(
    id: UUID,
    link_input_ports: LinkInputPortsToDataProduct,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> LinkInputPortsToDataProductPost:
    return LinkInputPortsToDataProductPost(
        input_port_links=request_input_ports_for_data_product(
            id,
            RequestInputPortsForDataProductRequest(
                output_ports=link_input_ports.input_ports,
                justification=link_input_ports.justification,
            ),
            background_tasks,
            authenticated_user=authenticated_user,
            db=db,
        ).input_port_links
    )


@router.post(
    "/{id}/input_ports",
    responses=_input_ports_responses,
    dependencies=_input_ports_dependencies,
)
def request_input_ports_for_data_product(
    id: UUID,
    body: RequestInputPortsForDataProductRequest,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> RequestInputPortsForDataProductResponse:
    input_ports = DataProductService(db).request_input_ports(
        id,
        body.output_ports,
        body.justification,
        actor=authenticated_user,
    )

    event_ids = EventService(db).create_events(
        [
            CreateEvent(
                name=(
                    EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED
                    if dataset_link.status == DecisionStatus.PENDING
                    else EventType.DATA_PRODUCT_DATASET_LINK_APPROVED
                ),
                subject_id=dataset_link.consuming_abstract_data_product_id,
                subject_type=EventReferenceEntity.DATA_PRODUCT,
                target_id=dataset_link.output_port_id,
                target_type=EventReferenceEntity.DATASET,
                actor_id=authenticated_user.id,
            )
            for dataset_link in input_ports
        ]
    )
    for dataset_link, event_id in zip(input_ports, event_ids):
        if dataset_link.status == DecisionStatus.APPROVED:
            NotificationService(db).create_data_product_notifications(
                data_product_id=dataset_link.consuming_abstract_data_product_id,
                event_id=event_id,
            )

    DataProductService(db).send_input_port_requested_emails_to_output_port_owners(
        input_ports, background_tasks, authenticated_user
    )
    RefreshInfrastructureLambda().trigger()
    return RequestInputPortsForDataProductResponse(
        input_port_links=[dataset_link.id for dataset_link in input_ports]
    )


@router.post(
    "/{id}/input_ports/{output_port_id}/renew",
    responses=_input_ports_responses,
    dependencies=_input_ports_dependencies,
)
def renew_input_port_for_data_product(
    id: UUID,
    output_port_id: UUID,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> RenewInputPortForDataProductResponse:
    input_port = DataProductService(db).renew_input_port(
        id, output_port_id, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=(
                EventType.DATA_PRODUCT_DATASET_LINK_REQUESTED
                if input_port.status == DecisionStatus.PENDING
                else EventType.DATA_PRODUCT_DATASET_LINK_APPROVED
            ),
            subject_id=input_port.consuming_abstract_data_product_id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=input_port.output_port_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )
    if input_port.status == DecisionStatus.APPROVED:
        NotificationService(db).create_data_product_notifications(
            data_product_id=input_port.consuming_abstract_data_product_id,
            event_id=event_id,
        )

    DataProductService(db).send_input_port_requested_emails_to_output_port_owners(
        [input_port], background_tasks, authenticated_user
    )
    RefreshInfrastructureLambda().trigger()
    return RenewInputPortForDataProductResponse(input_port_link=input_port.id)


@router.get("")
def get_data_products(
    db: Session = Depends(get_db_session),
    filter_to_user_with_assigment: Annotated[
        UUID | SkipJsonSchema[None], Query()
    ] = None,
) -> GetDataProductsResponse:
    return GetDataProductsResponse(
        data_products=[
            GetDataProductsResponseItem.model_validate(dp)
            for dp in DataProductService(db).get_data_products(
                filter_to_user_with_assigment
            )
        ]
    )


@router.get("/{id}/history")
def get_data_product_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetEventHistoryResponse:
    return GetEventHistoryResponse(
        events=[
            GetEventHistoryResponseItemOld.model_validate(event).convert()
            for event in EventService(db).get_history(
                id, EventReferenceEntity.DATA_PRODUCT
            )
        ]
    )


@router.get("/{id}")
def get_data_product(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductResponse:
    return DataProductService(db).get_data_product(id)


@router.get("/{id}/input_ports")
def get_data_product_input_ports(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> GetDataProductInputPortsResponse:
    return GetDataProductInputPortsResponse(
        input_ports=[
            AbstractDataProductInputPort.model_validate(input_port)
            for input_port in DataProductService(db).get_input_ports(id)
        ]
    )


@router.get("/{id}/rolled_up_tags")
def get_data_product_rolled_up_tags(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductRolledUpTagsResponse:
    return GetDataProductRolledUpTagsResponse(
        rolled_up_tags=DataProductService(db).get_rolled_up_tags(id)
    )


@router.delete(
    "/{id}/input_ports/{output_port_id}",
    responses={
        400: {
            "description": "Output port not found",
            "content": {
                "application/json": {"example": {"detail": "Output port not found"}}
            },
        },
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__REVOKE_OUTPUT_PORT_ACCESS,
                DataProductResolver,
            )
        ),
    ],
)
def unlink_input_port_from_data_product(
    id: UUID,
    output_port_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_dataset = DataProductService(db).remove_input_port(id, output_port_id)

    event_id = EventService(db).create_event(
        CreateEvent(
            name=(
                EventType.DATA_PRODUCT_DATASET_LINK_REMOVED
                if data_product_dataset.status != DecisionStatus.APPROVED
                else EventType.DATA_PRODUCT_DATASET_LINK_DENIED
            ),
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=data_product_dataset.output_port_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    if data_product_dataset.status == DecisionStatus.APPROVED:
        NotificationService(db).create_data_product_notifications(
            data_product_id=id, event_id=event_id
        )
    RefreshInfrastructureLambda().trigger()


@router.get("/{id}/settings")
def get_data_product_settings(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductSettingsResponse:
    return GetDataProductSettingsResponse(
        data_product_settings=DataProductService(db).get_data_product_settings(id)
    )
