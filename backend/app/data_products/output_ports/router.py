from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.authorization.role_assignments.enums import DecisionStatus
from app.authorization.role_assignments.output_port.auth import DatasetAuthAssignment
from app.authorization.role_assignments.output_port.schema import (
    UpdateRoleAssignment,
)
from app.authorization.role_assignments.output_port.service import RoleAssignmentService
from app.authorization.roles.schema import Prototype, Scope
from app.authorization.roles.service import RoleService
from app.configuration.data_product_settings.service import DataProductSettingService
from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DatasetResolver
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
)
from app.data_products.output_ports.curated_queries.router import (
    router as curated_queries_router,
)
from app.data_products.output_ports.model import Dataset as OutputPortModel
from app.data_products.output_ports.model import ensure_dataset_exists
from app.data_products.output_ports.query_stats.router import (
    router as query_stats_router,
)
from app.data_products.output_ports.schema_request import (
    CreateOutputPortRequest,
    DatasetAboutUpdate,
    DatasetCreate,
    DatasetStatusUpdate,
    DatasetUpdate,
    DatasetUsageUpdate,
)
from app.data_products.output_ports.schema_response import (
    CreateOutputPortResponse,
    DatasetGet,
    DatasetsGet,
    GetDataProductOutputPortsResponse,
    GetOutputPortResponse,
    UpdateOutputPortResponse,
)
from app.data_products.output_ports.service import OutputPortService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import (
    GetEventHistoryResponse,
    GetEventHistoryResponseItemOld,
)
from app.events.service import EventService
from app.graph.graph import Graph
from app.resource_names.service import ResourceNameService
from app.users.model import User
from app.users.notifications.service import NotificationService


def _assign_owner_role_assignments(
    dataset_id: UUID, owners: Sequence[UUID], db: Session, actor: User
) -> None:
    owner_role = RoleService(db).find_prototype(Scope.DATASET, Prototype.OWNER)
    if owner_role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner role not found",
        )

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
            UpdateRoleAssignment(id=assignment.id, decision=DecisionStatus.APPROVED),
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
old_route = "/datasets"
route = "/v2/data_products/{data_product_id}/output_ports"
router.include_router(query_stats_router)
router.include_router(curated_queries_router)


@router.get(f"{old_route}/namespace_suggestion", deprecated=True)
def get_dataset_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return NamespaceSuggestion(
        namespace=ResourceNameService.resource_name_suggestion(name).resource_name
    )


@router.get(f"{old_route}/validate_namespace", deprecated=True)
def validate_dataset_namespace(
    namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return NamespaceValidation(
        validity=ResourceNameService(model=OutputPortModel)
        .validate_resource_name(namespace, db)
        .validity
    )


@router.get(f"{old_route}/namespace_length_limits", deprecated=True)
def get_dataset_namespace_length_limits() -> NamespaceLengthLimits:
    return NamespaceLengthLimits(
        max_length=ResourceNameService.resource_name_length_limits().max_length
    )


@router.get(f"{old_route}/user/{{user_id}}", deprecated=True)
def get_user_datasets_old(
    user_id: UUID,  # This is deprecated
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[DatasetsGet]:
    return OutputPortService(db).get_datasets(
        authenticated_user, check_user_assigned=True
    )


## Also deprecated, let's see if we can remove that inbox or do something useful with it
@router.get(f"{old_route}/user", deprecated=True)
def get_user_datasets(
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Sequence[DatasetsGet]:
    return OutputPortService(db).get_datasets(
        authenticated_user, check_user_assigned=True
    )


@router.get(old_route, deprecated=True)
def get_datasets(
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[DatasetsGet]:
    return OutputPortService(db).get_datasets(user)


@router.get(route)
def get_data_product_output_ports(
    data_product_id: UUID, db: Session = Depends(get_db_session)
) -> GetDataProductOutputPortsResponse:
    return GetDataProductOutputPortsResponse(
        output_ports=OutputPortService(db).get_output_ports(data_product_id)
    )


@router.get(f"{old_route}/{{id}}", deprecated=True)
def get_dataset(
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> DatasetGet:
    return OutputPortService(db).get_dataset(id, user)


@router.get(f"{route}/{{id}}")
def get_output_port(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> GetOutputPortResponse:
    return DatasetGet.model_validate(
        OutputPortService(db).get_dataset(id, user, data_product_id)
    ).convert()


@router.get(f"{old_route}/{{id}}/history", deprecated=True)
def get_event_history_old(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[GetEventHistoryResponseItemOld]:
    ds = ensure_dataset_exists(id, db)
    return EventService(db).get_history(ds.id, EventReferenceEntity.DATASET)


@router.get(f"{route}/{{id}}/history")
def get_output_ports_event_history(
    data_product_id: UUID, id: UUID, db: Session = Depends(get_db_session)
) -> GetEventHistoryResponse:
    ds = ensure_dataset_exists(id, db, data_product_id=data_product_id)
    return GetEventHistoryResponse(
        events=[
            GetEventHistoryResponseItemOld.model_validate(ds).convert()
            for ds in EventService(db).get_history(ds.id, EventReferenceEntity.DATASET)
        ]
    )


@router.post(
    old_route,
    responses={
        200: {
            "description": "Dataset successfully created",
            "content": {
                "application/json": {"example": {"id": "random id of the new dataset"}}
            },
        },
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
    ],
    deprecated=True,
)
def create_dataset_old(
    dataset: DatasetCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateOutputPortResponse:
    return create_output_port(
        dataset.data_product_id, dataset.convert(), db, authenticated_user
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
    ],
)
def create_output_port(
    data_product_id: UUID,
    output_port: CreateOutputPortRequest,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> CreateOutputPortResponse:
    new_dataset = OutputPortService(db).create_dataset(data_product_id, output_port)
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
    f"{old_route}/{{id}}",
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
    ],
    deprecated=True,
)
def remove_dataset_old(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    ds = ensure_dataset_exists(id, db)
    return remove_dataset(ds.data_product_id, id, db, authenticated_user)


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
    ],
)
def remove_dataset(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    dataset = OutputPortService(db).remove_dataset(id, data_product_id)
    Authorization().clear_assignments_for_resource(resource_id=str(id))

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_REMOVED,
            actor_id=authenticated_user.id,
            subject_id=dataset.id,
            subject_type=EventReferenceEntity.DATASET,
            deleted_subject_identifier=dataset.name,
        ),
    )
    NotificationService(db).create_dataset_notifications(
        dataset_id=dataset.id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()


@router.put(
    f"{old_route}/{{id}}",
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        ),
    ],
    deprecated=True,
)
def update_dataset(
    id: UUID,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateOutputPortResponse:
    ds = ensure_dataset_exists(id, db)
    return update_output_port(ds.data_product_id, id, dataset, db, authenticated_user)


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
    ],
)
def update_output_port(
    data_product_id: UUID,
    id: UUID,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> UpdateOutputPortResponse:
    response = OutputPortService(db).update_dataset(id, data_product_id, dataset)

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
    f"{old_route}/{{id}}/about",
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        ),
    ],
    deprecated=True,
)
def update_dataset_about(
    id: UUID,
    dataset: DatasetAboutUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    ds = ensure_dataset_exists(id, db)
    return update_output_port_about(
        ds.data_product_id, id, dataset, db, authenticated_user
    )


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
    ],
)
def update_output_port_about(
    data_product_id: UUID,
    id: UUID,
    dataset: DatasetAboutUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    OutputPortService(db).update_dataset_about(id, data_product_id, dataset)

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    f"{old_route}/{{id}}/status",
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(Action.OUTPUT_PORT__UPDATE_STATUS, DatasetResolver)
        ),
    ],
    deprecated=True,
)
def update_dataset_status(
    id: UUID,
    dataset: DatasetStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    ds = ensure_dataset_exists(id, db)
    return update_output_port_status(
        ds.data_product_id, id, dataset, db, authenticated_user
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
    ],
)
def update_output_port_status(
    data_product_id: UUID,
    id: UUID,
    dataset: DatasetStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    OutputPortService(db).update_dataset_status(id, data_product_id, dataset)

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    f"{old_route}/{{id}}/usage",
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.OUTPUT_PORT__UPDATE_PROPERTIES, DatasetResolver
            )
        ),
    ],
    deprecated=True,
)
def update_dataset_usage(
    id: UUID,
    usage: DatasetUsageUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    OutputPortService(db).update_dataset_usage(id, usage)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )


@router.get(f"{old_route}/{{id}}/graph", deprecated=True)
def get_graph_data_old(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    ds = ensure_dataset_exists(id, db)
    return get_output_port_graph_data(ds.data_product_id, id, db, level)


@router.get(f"{route}/{{id}}/graph")
def get_output_port_graph_data(
    data_product_id: UUID,
    id: UUID,
    db: Session = Depends(get_db_session),
    level: int = 3,
) -> Graph:
    return OutputPortService(db).get_graph_data(id, data_product_id, level)


@router.post(
    f"{old_route}/{{id}}/settings/{{setting_id}}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.OUTPUT_PORT__UPDATE_SETTINGS, DatasetResolver)
        ),
    ],
    deprecated=True,
)
def set_value_for_dataset(
    id: UUID,
    setting_id: UUID,
    value: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    ds = ensure_dataset_exists(id, db)
    return set_value_for_output_port(
        ds.data_product_id, id, setting_id, value, db, authenticated_user
    )


@router.post(
    f"{route}/{{id}}/settings/{{setting_id}}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.OUTPUT_PORT__UPDATE_SETTINGS, DatasetResolver)
        ),
    ],
)
def set_value_for_output_port(
    data_product_id: UUID,
    id: UUID,
    setting_id: UUID,
    value: str,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    ensure_dataset_exists(id, db, data_product_id=data_product_id)
    DataProductSettingService(db).set_value_for_product(setting_id, id, value)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_SETTING_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
