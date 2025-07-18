from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DataOutputResolver
from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.core.namespace.validation import NamespaceLengthLimits, NamespaceSuggestion
from app.data_outputs import email
from app.data_outputs.schema_request import (
    DataOutputResultStringRequest,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_outputs.schema_response import DataOutputGet, DataOutputsGet
from app.data_outputs.service import DataOutputService
from app.database.database import get_db_session
from app.events.enums import EventReferenceEntity, EventType
from app.events.schema import CreateEvent
from app.events.schema_response import EventGet
from app.events.service import EventService
from app.graph.graph import Graph
from app.notifications.service import NotificationService
from app.role_assignments.dataset.service import RoleAssignmentService
from app.users.schema import User

router = APIRouter(prefix="/data_outputs", tags=["data_outputs"])


@router.get("")
def get_data_outputs(db: Session = Depends(get_db_session)) -> Sequence[DataOutputsGet]:
    return DataOutputService(db).get_data_outputs()


@router.get("/namespace_suggestion")
def get_data_output_namespace_suggestion(name: str) -> NamespaceSuggestion:
    return DataOutputService.data_output_namespace_suggestion(name)


@router.get("/namespace_length_limits")
def get_data_output_namespace_length_limits() -> NamespaceLengthLimits:
    return DataOutputService.data_output_namespace_length_limits()


@router.post("/result_string")
def get_data_output_result_string(
    request: DataOutputResultStringRequest, db: Session = Depends(get_db_session)
) -> str:
    return DataOutputService(db).get_data_output_result_string(request)


@router.get("/{id}")
def get_data_output(id: UUID, db: Session = Depends(get_db_session)) -> DataOutputGet:
    output = DataOutputService(db).get_data_output(id)
    if output is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Data output not found"
        )
    return output


@router.get("/{id}/history")
def get_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[EventGet]:
    return EventService(db).get_history(id, EventReferenceEntity.DATA_OUTPUT)


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "Data Output not found",
            "content": {
                "application/json": {"example": {"detail": "Data Output id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__DELETE_DATA_OUTPUT,
                DataOutputResolver,
            )
        ),
    ],
)
def remove_data_output(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_output = DataOutputService(db).remove_data_output(id)
    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_REMOVED,
            actor_id=authenticated_user.id,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            deleted_subject_identifier=data_output.name,
            target_id=data_output.owner_id,
            target_type=EventReferenceEntity.DATA_PRODUCT,
            deleted_target_identifier=data_output.owner.name,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=data_output.owner_id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()


@router.put(
    "/{id}",
    responses={
        404: {
            "description": "Data Output not found",
            "content": {
                "application/json": {"example": {"detail": "Data Output id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                DataOutputResolver,
            )
        ),
    ],
)
def update_data_output(
    id: UUID,
    data_output: DataOutputUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    result = DataOutputService(db).update_data_output(id, data_output)
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        )
    )
    RefreshInfrastructureLambda().trigger()
    return result


@router.put(
    "/{id}/status",
    responses={
        404: {
            "description": "Data Output not found",
            "content": {
                "application/json": {"example": {"detail": "Data Output id not found"}}
            },
        }
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                Action.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                DataOutputResolver,
            )
        ),
    ],
)
def update_data_output_status(
    id: UUID,
    data_output: DataOutputStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    DataOutputService(db).update_data_output_status(
        id, data_output, actor=authenticated_user
    )
    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_UPDATED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            actor_id=authenticated_user.id,
        )
    )


@router.post(
    "/{id}/dataset/{dataset_id}",
    responses={
        400: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset not found"}}
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
                Action.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                DataOutputResolver,
            )
        ),
    ],
)
def link_dataset_to_data_output(
    id: UUID,
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    dataset_link = DataOutputService(db).link_dataset_to_data_output(
        id, dataset_id, actor=authenticated_user
    )

    EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_REQUESTED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            target_id=dataset_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    RefreshInfrastructureLambda().trigger()

    approvers = RoleAssignmentService(db).users_with_authz_action(
        dataset_link.dataset_id, Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST
    )
    background_tasks.add_task(
        email.send_link_dataset_email(
            dataset_link.dataset,
            dataset_link.data_output,
            requester=authenticated_user,
            approvers=approvers,
        )
    )
    return {"id": dataset_link.id}


@router.delete(
    "/{id}/dataset/{dataset_id}",
    responses={
        400: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset not found"}}
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
                Action.DATA_PRODUCT__REVOKE_DATASET_ACCESS,
                DataOutputResolver,
            )
        ),
    ],
)
def unlink_dataset_from_data_output(
    id: UUID,
    dataset_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    data_output = DataOutputService(db).unlink_dataset_from_data_output(id, dataset_id)

    event_id = EventService(db).create_event(
        CreateEvent(
            name=EventType.DATA_OUTPUT_DATASET_LINK_REMOVED,
            subject_id=id,
            subject_type=EventReferenceEntity.DATA_OUTPUT,
            target_id=dataset_id,
            target_type=EventReferenceEntity.DATASET,
            actor_id=authenticated_user.id,
        ),
    )
    NotificationService(db).create_data_product_notifications(
        data_product_id=data_output.owner_id, event_id=event_id
    )
    RefreshInfrastructureLambda().trigger()


@router.get("/{id}/graph")
def get_graph_data(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    return DataOutputService(db).get_graph_data(id, level)
