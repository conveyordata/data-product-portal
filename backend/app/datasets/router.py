from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DatasetResolver
from app.core.authz.resolvers import EmptyResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
)
from app.data_product_settings.service import DataProductSettingService
from app.database.database import get_db_session
from app.datasets.schema_request import (
    DatasetAboutUpdate,
    DatasetCreate,
    DatasetStatusUpdate,
    DatasetUpdate,
)
from app.datasets.schema_response import DatasetGet, DatasetsGet
from app.datasets.service import DatasetService
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import EventGet
from app.events.service import EventService
from app.graph.graph import Graph
from app.notifications.service import NotificationService
from app.role_assignments.dataset.schema import (
    CreateRoleAssignment,
    UpdateRoleAssignment,
)
from app.role_assignments.dataset.service import RoleAssignmentService
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Prototype, Scope
from app.roles.service import RoleService
from app.users.model import User

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def get_datasets(
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[DatasetsGet]:
    return DatasetService(db).get_datasets(user)


@router.get("/namespace_suggestion")
def get_dataset_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return DatasetService.dataset_namespace_suggestion(name)


@router.get("/validate_namespace")
def validate_dataset_namespace(
    namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return DatasetService(db).validate_dataset_namespace(namespace)


@router.get("/namespace_length_limits")
def get_dataset_namespace_length_limits() -> NamespaceLengthLimits:
    return DatasetService.dataset_namespace_length_limits()


@router.get("/{id}")
def get_dataset(
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> DatasetGet:
    return DatasetService(db).get_dataset(id, user)


@router.get("/user/{user_id}")
def get_user_datasets(
    user_id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[DatasetsGet]:
    return DatasetService(db).get_user_datasets(user_id)


@router.get("/{id}/history")
def get_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[EventGet]:
    return EventService(db).get_history(id, EventReferenceEntity.DATASET)


@router.post(
    "",
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
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_DATASET, EmptyResolver)),
    ],
)
def create_dataset(
    dataset: DatasetCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    new_dataset = DatasetService(db).create_dataset(dataset)
    _assign_owner_role_assignments(
        new_dataset.id, dataset.owners, db=db, actor=authenticated_user
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
    return {"id": new_dataset.id}


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
            CreateRoleAssignment(
                user_id=owner_id,
                role_id=owner_role.id,
            ),
            actor=actor,
        )
        assignment_service.update_assignment(
            UpdateRoleAssignment(id=assignment.id, decision=DecisionStatus.APPROVED),
            actor=actor,
        )
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


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(Authorization.enforce(Action.DATASET__DELETE, DatasetResolver)),
    ],
)
def remove_dataset(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    dataset = DatasetService(db).remove_dataset(id)
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
    "/{id}",
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
            Authorization.enforce(Action.DATASET__UPDATE_PROPERTIES, DatasetResolver)
        ),
    ],
)
def update_dataset(
    id: UUID,
    dataset: DatasetUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    response = DatasetService(db).update_dataset(id, dataset)

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
    return response


@router.put(
    "/{id}/about",
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
            Authorization.enforce(Action.DATASET__UPDATE_PROPERTIES, DatasetResolver)
        ),
    ],
)
def update_dataset_about(
    id: UUID,
    dataset: DatasetAboutUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DatasetService(db).update_dataset_about(id, dataset)

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )


@router.put(
    "/{id}/status",
    responses={
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        }
    },
    dependencies=[
        Depends(Authorization.enforce(Action.DATASET__UPDATE_STATUS, DatasetResolver)),
    ],
)
def update_dataset_status(
    id: UUID,
    dataset: DatasetStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DatasetService(db).update_dataset_status(id, dataset)

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATASET_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        )
    )


@router.get("/{id}/graph")
def get_graph_data(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    return DatasetService(db).get_graph_data(id, level)


@router.post(
    "/{id}/settings/{setting_id}",
    dependencies=[
        Depends(
            Authorization.enforce(Action.DATASET__UPDATE_SETTINGS, DatasetResolver)
        ),
    ],
)
def set_value_for_dataset(
    id: UUID,
    setting_id: UUID,
    value: str,
    db: Session = Depends(get_db_session),
) -> None:
    return DataProductSettingService(db).set_value_for_product(setting_id, id, value)
