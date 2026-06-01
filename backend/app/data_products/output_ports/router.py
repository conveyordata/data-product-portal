from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.auth import DatasetAuthAssignment
from app.authorization.role_assignments.output_port.schema import (
    UpdateOutputPortRoleAssignment,
)
from app.authorization.role_assignments.output_port.service import RoleAssignmentService
from app.authorization.roles.schema import Prototype, Scope
from app.authorization.roles.service import RoleService
from app.configuration.data_product_settings.service import DataProductSettingService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DatasetResolver
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.webhooks.events import (
    OutputPortAboutUpdatedEvent,
    OutputPortCreatedEvent,
    OutputPortDeletedEvent,
    OutputPortSettingChangedEvent,
    OutputPortStatusUpdatedEvent,
    OutputPortUpdatedEvent,
)
from app.core.webhooks.v2 import _emits_event
from app.data_products.output_ports.contract.router import (
    router as contract_router,
)
from app.data_products.output_ports.curated_queries.router import (
    router as curated_queries_router,
)
from app.data_products.output_ports.data_quality.router import (
    router as data_quality_router,
)
from app.data_products.output_ports.enums import OutputPortAccessType
from app.data_products.output_ports.model import ensure_output_port_exists
from app.data_products.output_ports.query_stats.router import (
    router as query_stats_router,
)
from app.data_products.output_ports.schema_request import (
    CreateOutputPortRequest,
    DatasetAboutUpdate,
    DatasetStatusUpdate,
    DatasetUpdate,
)
from app.data_products.output_ports.schema_response import (
    CreateOutputPortResponse,
    GetDataProductOutputPortsResponse,
    GetOutputPortResponse,
    UpdateOutputPortResponse,
)
from app.data_products.output_ports.service import OutputPortService
from app.data_products.schema_response import GetDataProductResponse
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
from app.users.model import User
from app.users.notifications.service import NotificationService


def _assign_owner_role_assignments(
    dataset_id: UUID, owners: Sequence[UUID], db: Session, actor: User
) -> None:
    owner_role = RoleService(db).find_prototype(Scope.DATASET, Prototype.OWNER)

    assignment_service = RoleAssignmentService(db)
    event_service = EventService(db)
    for owner_id in owners:
        assignment = assignment_service.create_assignment(
            dataset_id,
            user_id=owner_id,
            role_id=owner_role.id,
            actor=actor,
        )
        assignment = assignment_service.update_assignment(
            UpdateOutputPortRoleAssignment(
                id=assignment.id, decision=DecisionStatus.APPROVED
            ),
            actor=actor,
        )
        DatasetAuthAssignment(assignment).add()
        event_service.create_event(
            CreateEvent(
                name=EventType.DATASET_ROLE_ASSIGNMENT_CREATED,
                subject_id=assignment.dataset_id,
                subject_type=EventReferenceEntity.DATASET,
                target_id=assignment.user_id,
                target_type=EventReferenceEntity.USER,
                actor_id=actor.id,
            )
        )


router = APIRouter(tags=["Data Products - Output ports"])
route = "/v2/data_products/{data_product_id}/output_ports"
router.include_router(query_stats_router)
router.include_router(curated_queries_router)
router.include_router(data_quality_router)
router.include_router(contract_router)


@router.get(route)
def get_data_product_output_ports(
    data_product_id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> GetDataProductOutputPortsResponse:
    return GetDataProductOutputPortsResponse(
        output_ports=OutputPortService(db).get_output_ports(data_product_id, user)
    )


@router.get(f"{route}/{{id}}", response_model=GetOutputPortResponse)
def get_output_port(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
):
    return OutputPortService(db).get_visible_dataset(id, user, data_product_id)


@router.get(f"{route}/{{id}}/history")
def get_output_ports_event_history(
    data_product_id: UUID, id: UUID, db: Session = Depends(get_db_session)
) -> GetEventHistoryResponse:
    ds = ensure_output_port_exists(id, db, data_product_id=data_product_id)
    return GetEventHistoryResponse(
        events=[
            GetEventHistoryResponseItemOld.model_validate(ds).convert()
            for ds in EventService(db).get_history(ds.id, EventReferenceEntity.DATASET)
        ]
    )


@router.post(
    route,
    responses={
        404: {
            "description": "Owner not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User email for owner not found"}
                }
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.GLOBAL__CREATE_OUTPUT_PORT, EmptyResolver)
        ),
        Depends(_emits_event(OutputPortCreatedEvent)),
    ],
)
def create_output_port(
    request: Request,
    data_product_id: UUID,
    output_port: CreateOutputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateOutputPortResponse:
    # Temporarily convert public to unrestricted.
    if output_port.access_type == OutputPortAccessType.PUBLIC:
        output_port.access_type = OutputPortAccessType.UNRESTRICTED

    new_dataset = OutputPortService(db).create_dataset(data_product_id, output_port)
    request.state.event = OutputPortCreatedEvent(
        data_product=GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        output_port=GetOutputPortResponse.model_validate(
            OutputPortService(db).get_dataset(new_dataset.id, data_product_id)
        ),
    )
    _assign_owner_role_assignments(
        new_dataset.id, output_port.owners, db=db, actor=authenticated_user
    )

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_CREATED,
            subject_id=new_dataset.id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=new_dataset.id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()
    return CreateOutputPortResponse(id=new_dataset.id)


@router.delete(
    f"{route}/{{id}}",
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(Authorization.enforce(Action.OUTPUT_PORT__DELETE, DatasetResolver)),
        Depends(_emits_event(OutputPortDeletedEvent)),
    ],
)
def remove_output_port(
    request: Request,
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    output_port_for_event = OutputPortService(db).get_dataset(id, data_product_id)
    request.state.event = OutputPortDeletedEvent(
        data_product=GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        output_port=GetOutputPortResponse.model_validate(output_port_for_event),
    )
    dataset = OutputPortService(db).remove_dataset(id, data_product_id)
    Authorization().clear_assignments_for_resource(resource_id=str(id))

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_REMOVED,
            actor_id=authenticated_user.id,
            subject_id=dataset.id,
            subject_type=EventReferenceEntity.DATASET,
            deleted_subject_identifier=dataset.name,
            target_id=dataset.data_product_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=dataset.id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()


@router.put(
    f"{route}/{{id}}",
    responses={
        404: {
            "description": "Output port not found",
            "content": {
                "application/json": {"example": {"detail": "Output port id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        ),
        Depends(_emits_event(OutputPortUpdatedEvent)),
    ],
)
def update_output_port(
    request: Request,
    data_product_id: UUID,
    id: UUID,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateOutputPortResponse:
    # Temporarily convert public to unrestricted.
    if dataset.access_type == OutputPortAccessType.PUBLIC:
        dataset.access_type = OutputPortAccessType.UNRESTRICTED

    response = OutputPortService(db).update_dataset(id, data_product_id, dataset)
    request.state.event = OutputPortUpdatedEvent(
        data_product=GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        output_port=GetOutputPortResponse.model_validate(
            OutputPortService(db).get_dataset(id, data_product_id)
        ),
    )

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
    return UpdateOutputPortResponse(id=response)


@router.put(
    f"{route}/{{id}}/about",
    responses={
        404: {
            "description": "Output port not found",
            "content": {
                "application/json": {"example": {"detail": "Output port id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        ),
        Depends(_emits_event(OutputPortAboutUpdatedEvent)),
    ],
)
def update_output_port_about(
    request: Request,
    data_product_id: UUID,
    id: UUID,
    dataset: DatasetAboutUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    OutputPortService(db).update_dataset_about(id, data_product_id, dataset)
    request.state.event = OutputPortAboutUpdatedEvent(
        data_product=GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        output_port=GetOutputPortResponse.model_validate(
            OutputPortService(db).get_dataset(id, data_product_id)
        ),
    )

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    f"{route}/{{id}}/status",
    responses={
        404: {
            "description": "Output port not found",
            "content": {
                "application/json": {"example": {"detail": "Output port id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.OUTPUT_PORT__UPDATE_STATUS, DatasetResolver)
        ),
        Depends(_emits_event(OutputPortStatusUpdatedEvent)),
    ],
)
def update_output_port_status(
    request: Request,
    data_product_id: UUID,
    id: UUID,
    dataset: DatasetStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    OutputPortService(db).update_dataset_status(id, data_product_id, dataset)
    request.state.event = OutputPortStatusUpdatedEvent(
        data_product=GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        output_port=GetOutputPortResponse.model_validate(
            OutputPortService(db).get_dataset(id, data_product_id)
        ),
    )

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )


@router.get(f"{route}/{{id}}/graph")
def get_output_port_graph_data(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    level: int = 3,
) -> Graph:
    return OutputPortService(db).get_graph_data(id, data_product_id, level)


@router.post(
    f"{route}/{{id}}/settings/{{setting_id}}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.OUTPUT_PORT__UPDATE_SETTINGS, DatasetResolver)
        ),
        Depends(_emits_event(OutputPortSettingChangedEvent)),
    ],
)
def set_value_for_output_port(
    request: Request,
    data_product_id: UUID,
    id: UUID,
    setting_id: UUID,
    value: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    ensure_output_port_exists(id, db, data_product_id=data_product_id)
    DataProductSettingService(db).set_value_for_product(setting_id, id, value)
    request.state.event = OutputPortSettingChangedEvent(
        data_product=GetDataProductResponse.model_validate(
            DataProductService(db).get_data_product(data_product_id)
        ),
        output_port=GetOutputPortResponse.model_validate(
            OutputPortService(db).get_dataset(id, data_product_id)
        ),
    )
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_SETTING_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
