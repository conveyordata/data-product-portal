from copy import deepcopy
from typing import Optional, Sequence
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from sqlalchemy.orm import Session

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
from app.authorization.role_assignments.output_port.service import (
    RoleAssignmentService as DatasetRoleAssignmentService,
)
from app.authorization.roles.schema import Prototype, Scope
from app.authorization.roles.service import RoleService
from app.configuration.data_product_settings.service import DataProductSettingService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataProductResolver
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.webhooks.v2 import emit_event, emit_event_after
from app.data_products import email
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.input_ports.model import (
    DataProductDatasetAssociation,
)
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_request import (
    DataProductAboutUpdate,
    DataProductCreate,
    DataProductStatusUpdate,
    DataProductUpdate,
    DataProductUsageUpdate,
    LinkInputPortsToDataProduct,
)
from app.data_products.schema_response import (
    CreateDataProductResponse,
    DataProductsGet,
    DatasetLinks,
    GetDataProductInputPortsResponse,
    GetDataProductResponse,
    GetDataProductRolledUpTagsResponse,
    GetDataProductSettingsResponse,
    GetDataProductsResponse,
    LinkInputPortsToDataProductPost,
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

_emit_data_product_created = emit_event_after(
    "data_product.created",
    lambda request, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(request.state.data_product_id)
        )
    },
)
_emit_data_product_updated = emit_event_after(
    "data_product.updated",
    lambda id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(id)
        )
    },
)
_emit_data_product_deleted = emit_event(
    "data_product.deleted",
    lambda id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(id)
        )
    },
)
_emit_data_product_about_updated = emit_event_after(
    "data_product.about_updated",
    lambda id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(id)
        )
    },
)
_emit_data_product_status_updated = emit_event_after(
    "data_product.status_updated",
    lambda id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(id)
        )
    },
)
_emit_data_product_setting_changed = emit_event_after(
    "data_product.setting_changed",
    lambda id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(id)
        )
    },
)
_emit_data_product_input_port_linked = emit_event_after(
    "data_product.input_port_linked",
    lambda id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(id)
        )
    },
)
_emit_data_product_input_port_unlinked = emit_event_after(
    "data_product.input_port_unlinked",
    lambda id, db, **_: {
        "data_product": GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(id)
        )
    },
)

router = APIRouter()


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
        Depends(_emit_data_product_created),
    ],
)
def create_data_product(
    request: Request,
    data_product: DataProductCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateDataProductResponse:
    created_data_product = DataProductService(db).create_data_product(data_product)
    request.state.data_product_id = created_data_product.id
    owners = data_product.owners
    _assign_owner_role_assignments(
        created_data_product.id,
        owners=owners,
        db=db,
        actor=authenticated_user,
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_CREATED,
            subject_id=created_data_product.id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=created_data_product.id,
        event_id=event_id,
        extra_receiver_ids=owners,
    )
    RefreshInfrastructureLambda().trigger()
    OutputPortService(db).recalculate_search_for_output_ports_of_product(
        created_data_product.id
    )
    return CreateDataProductResponse(id=created_data_product.id)


def _assign_owner_role_assignments(
    data_product_id: UUID, owners: Sequence[UUID], db: Session, actor: User
) -> None:
    owner_role = RoleService(db).find_prototype(Scope.DATA_PRODUCT, Prototype.OWNER)
    if not owner_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner role not found",
        )

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
        404: {
            "description": "Data Product not found",
            "content": {
                "application/json": {"example": {"detail": "Data Product id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATA_PRODUCT__DELETE, DataProductResolver)
        ),
        Depends(_emit_data_product_deleted),
    ],
)
def remove_data_product(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
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
        Depends(_emit_data_product_updated),
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
        Depends(_emit_data_product_about_updated),
    ],
)
def update_data_product_about(
    id: UUID,
    data_product: DataProductAboutUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product = DataProductService(db).update_data_product_about(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=data_product.id,
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
        Depends(_emit_data_product_status_updated),
    ],
)
def update_data_product_status(
    id: UUID,
    data_product: DataProductStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product = DataProductService(db).update_data_product_status(id, data_product)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_PRODUCT_UPDATED,
            subject_id=data_product.id,
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


def _send_dataset_link_emails(
    dataset_links: list[DataProductDatasetAssociation],
    background_tasks: BackgroundTasks,
    actor: User,
    db: Session,
) -> None:
    for dataset_link in dataset_links:
        if dataset_link.dataset.access_type != OutputPortAccessType.UNRESTRICTED:
            approvers = DatasetRoleAssignmentService(db).users_with_authz_action(
                dataset_link.dataset_id,
                Action.OUTPUT_PORT__APPROVE_DATAPRODUCT_ACCESS_REQUEST,
            )
            background_tasks.add_task(
                email.send_dataset_link_email(
                    dataset_link.data_product,
                    dataset_link.dataset,
                    requester=deepcopy(actor),
                    approvers=[deepcopy(approver) for approver in approvers],
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
        Depends(_emit_data_product_setting_changed),
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


_router = router
router = APIRouter(tags=["Data Products"])
route = "/v2/data_products"

router.include_router(_router, prefix=route)


@router.post(
    f"{route}/{{id}}/link_input_ports",
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
                Action.DATA_PRODUCT__REQUEST_OUTPUT_PORT_ACCESS,
                DataProductResolver,
            )
        ),
        Depends(_emit_data_product_input_port_linked),
    ],
)
def link_input_ports_to_data_product(
    id: UUID,
    link_input_ports: LinkInputPortsToDataProduct,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> LinkInputPortsToDataProductPost:
    dataset_links = DataProductService(db).link_datasets_to_data_product(
        id,
        link_input_ports.input_ports,
        link_input_ports.justification,
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
                subject_id=dataset_link.data_product_id,
                subject_type=EventReferenceEntity.DATA_PRODUCT,
                target_id=dataset_link.dataset_id,
                target_type=EventReferenceEntity.DATASET,
                actor_id=authenticated_user.id,
            )
            for dataset_link in dataset_links
        ]
    )
    for dataset_link, event_id in zip(dataset_links, event_ids):
        if dataset_link.status == DecisionStatus.APPROVED:
            NotificationService(db).create_data_product_notifications(
                data_product_id=dataset_link.data_product_id, event_id=event_id
            )

    _send_dataset_link_emails(dataset_links, background_tasks, authenticated_user, db)
    RefreshInfrastructureLambda().trigger()
    return LinkInputPortsToDataProductPost(
        input_port_links=[dataset_link.id for dataset_link in dataset_links]
    )


@router.get(route)
def get_data_products(
    db: Session = Depends(get_db_session),
    filter_to_user_with_assigment: Optional[UUID] = Query(default=None),
) -> GetDataProductsResponse:
    return GetDataProductsResponse(
        data_products=[
            DataProductsGet.model_validate(data_product_old).convert()
            for data_product_old in DataProductService(db).get_data_products(
                filter_to_user_with_assigment
            )
        ]
    )


@router.get(f"{route}/{{id}}/history")
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


@router.get(f"{route}/{{id}}")
def get_data_product(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductResponse:
    return DataProductService(db).get_data_product(id)


@router.get(f"{route}/{{id}}/input_ports")
def get_data_product_input_ports(
    id: UUID,
    db: Session = Depends(get_db_session),
) -> GetDataProductInputPortsResponse:
    return GetDataProductInputPortsResponse(
        input_ports=[
            DatasetLinks.model_validate(input_port).convert()
            for input_port in DataProductService(db).get_input_ports(id)
        ]
    )


@router.get(f"{route}/{{id}}/rolled_up_tags")
def get_data_product_rolled_up_tags(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductRolledUpTagsResponse:
    return GetDataProductRolledUpTagsResponse(
        rolled_up_tags=DataProductService(db).get_rolled_up_tags(id)
    )


@router.delete(
    f"{route}/{{id}}/input_ports/{{input_port_id}}",
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
        Depends(_emit_data_product_input_port_unlinked),
    ],
)
def unlink_input_port_from_data_product(
    id: UUID,
    input_port_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_product_dataset = DataProductService(db).unlink_dataset_from_data_product(
        id, input_port_id
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=(
                EventType.DATA_PRODUCT_DATASET_LINK_REMOVED
                if data_product_dataset.status != DecisionStatus.APPROVED
                else EventType.DATA_PRODUCT_DATASET_LINK_DENIED
            ),
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_PRODUCT,
            target_id=data_product_dataset.dataset_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    if data_product_dataset.status == DecisionStatus.APPROVED:
        NotificationService(db).create_data_product_notifications(
            data_product_id=id, event_id=event_id
        )
    RefreshInfrastructureLambda().trigger()


@router.get(f"{route}/{{id}}/settings")
def get_data_product_settings(
    id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductSettingsResponse:
    return GetDataProductSettingsResponse(
        data_product_settings=DataProductService(db).get_data_product_settings(id)
    )
