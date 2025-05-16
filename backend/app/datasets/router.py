from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DatasetResolver
from app.core.namespace.validation import (
    NamespaceLengthLimits,
    NamespaceSuggestion,
    NamespaceValidation,
)
from app.data_product_settings.service import DataProductSettingService
from app.database.database import get_db_session
from app.datasets.schema_request import (
    DatasetAboutUpdate,
    DatasetCreateUpdate,
    DatasetStatusUpdate,
)
from app.datasets.schema_response import DatasetGet, DatasetsGet
from app.datasets.service import DatasetService
from app.dependencies import only_dataset_owners
from app.events.schema_response import EventGet
from app.graph.graph import Graph
from app.role_assignments.dataset.router import create_assignment, decide_assignment
from app.role_assignments.dataset.schema import (
    CreateRoleAssignment,
    DecideRoleAssignment,
)
from app.role_assignments.enums import DecisionStatus
from app.roles.schema import Scope
from app.roles.service import RoleService
from app.users.model import User

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def get_datasets(
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> Sequence[DatasetsGet]:
    return DatasetService().get_datasets(db, user)


@router.get("/namespace_suggestion")
async def get_dataset_namespace_suggestion(
    name: str, db: Session = Depends(get_db_session)
) -> NamespaceSuggestion:
    return DatasetService().dataset_namespace_suggestion(name, db)


@router.get("/validate_namespace")
async def validate_dataset_namespace(
    namespace: str, db: Session = Depends(get_db_session)
) -> NamespaceValidation:
    return DatasetService().validate_dataset_namespace(namespace, db)


@router.get("/namespace_length_limits")
async def get_dataset_namespace_length_limits() -> NamespaceLengthLimits:
    return DatasetService().dataset_namespace_length_limits()


@router.get("/{id}")
def get_dataset(
    id: UUID,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_authenticated_user),
) -> DatasetGet:
    return DatasetService().get_dataset(id, db, user)


@router.get("/user/{user_id}")
def get_user_datasets(
    user_id: UUID, db: Session = Depends(get_db_session)
) -> Sequence[DatasetsGet]:
    return DatasetService().get_user_datasets(user_id, db)


@router.get("/{id}/history")
def get_event_history(
    id: UUID, db: Session = Depends(get_db_session)
) -> list[EventGet]:
    return DatasetService().get_event_history(id, db)


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
        Depends(Authorization.enforce(Action.GLOBAL__CREATE_DATASET, DatasetResolver)),
    ],
)
def create_dataset(
    dataset: DatasetCreateUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    new_dataset = DatasetService().create_dataset(dataset, db, authenticated_user)
    owner_role = [
        role
        for role in RoleService(db).get_roles(Scope.DATASET)
        if role.name.lower() == "owner"
    ]
    if len(owner_role) == 1:
        owner_role = owner_role[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner role not found",
        )
    for owner in new_dataset.owners:
        resp = create_assignment(
            CreateRoleAssignment(
                dataset_id=new_dataset.id, user_id=owner.id, role_id=owner_role.id
            ),
            db,
            authenticated_user,
        )
        decide_assignment(
            id=resp.id,
            background_tasks=background_tasks,
            request=DecideRoleAssignment(decision=DecisionStatus.APPROVED),
            db=db,
            user=authenticated_user,
        )

    return {"id": new_dataset.id}


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
        Depends(only_dataset_owners),
        Depends(Authorization.enforce(Action.DATASET__DELETE, DatasetResolver)),
    ],
)
def remove_dataset(
    id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    DatasetService().remove_dataset(id, db, authenticated_user)
    background_tasks.add_task(
        Authorization().clear_assignments_for_resource,
        resource_id=str(id),
    )
    return


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
        Depends(only_dataset_owners),
        Depends(
            Authorization.enforce(Action.DATASET__UPDATE_PROPERTIES, DatasetResolver)
        ),
    ],
)
def update_dataset(
    id: UUID,
    dataset: DatasetCreateUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    return DatasetService().update_dataset(id, dataset, db, authenticated_user)


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
        Depends(only_dataset_owners),
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
    return DatasetService().update_dataset_about(id, dataset, db, authenticated_user)


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
        Depends(only_dataset_owners),
        Depends(Authorization.enforce(Action.DATASET__UPDATE_STATUS, DatasetResolver)),
    ],
)
def update_dataset_status(
    id: UUID,
    dataset: DatasetStatusUpdate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return DatasetService().update_dataset_status(id, dataset, db, authenticated_user)


@router.post(
    "/{id}/user/{user_id}",
    responses={
        400: {
            "description": "User not found",
            "content": {
                "application/json": {"example": {"detail": "User email not found"}}
            },
        },
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        },
    },
    dependencies=[
        Depends(only_dataset_owners),
        Depends(Authorization.enforce(Action.DATASET__CREATE_USER, DatasetResolver)),
    ],
)
def add_user_to_dataset(
    id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return DatasetService().add_user_to_dataset(id, user_id, db, authenticated_user)


@router.delete(
    "/{id}/user/{user_id}",
    responses={
        400: {
            "description": "User not found",
            "content": {
                "application/json": {"example": {"detail": "User email not found"}}
            },
        },
        404: {
            "description": "Dataset not found",
            "content": {
                "application/json": {"example": {"detail": "Dataset id not found"}}
            },
        },
    },
    dependencies=[
        Depends(only_dataset_owners),
        Depends(Authorization.enforce(Action.DATASET__DELETE_USER, DatasetResolver)),
    ],
)
def remove_user_from_dataset(
    id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return DatasetService().remove_user_from_dataset(
        id, user_id, db, authenticated_user
    )


@router.get("/{id}/graph")
def get_graph_data(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    return DatasetService().get_graph_data(id, level, db)


@router.post(
    "/{id}/settings/{setting_id}",
    dependencies=[
        Depends(only_dataset_owners),
        Depends(
            Authorization.enforce(Action.DATASET__UPDATE_SETTINGS, DatasetResolver)
        ),
    ],
)
def set_value_for_dataset(
    id: UUID,
    setting_id: UUID,
    value: str,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> None:
    return DataProductSettingService().set_value_for_product(
        setting_id, id, value, authenticated_user, db
    )
