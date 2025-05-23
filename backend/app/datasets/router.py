from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz import Action, Authorization, DatasetResolver
from app.core.authz.resolvers import EmptyResolver
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
from app.graph.graph import Graph
from app.role_assignments.dataset.router import create_assignment, decide_assignment
from app.role_assignments.dataset.schema import (
    CreateRoleAssignment,
    DecideRoleAssignment,
)
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
def get_dataset_namespace_suggestion(
    name: str, db: Session = Depends(get_db_session)
) -> NamespaceSuggestion:
    return DatasetService(db).dataset_namespace_suggestion(name)


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
    owner_role = RoleService(db).find_prototype(Scope.DATASET, Prototype.OWNER)
    if owner_role is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Owner role not found",
        )

    new_dataset = DatasetService(db).create_dataset(dataset)
    for owner_id in dataset.owners:
        resp = create_assignment(
            new_dataset.id,
            CreateRoleAssignment(
                dataset_id=new_dataset.id, user_id=owner_id, role_id=owner_role.id
            ),
            db,
            authenticated_user,
        )
        decide_assignment(
            id=resp.id,
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
        Depends(Authorization.enforce(Action.DATASET__DELETE, DatasetResolver)),
    ],
)
def remove_dataset(id: UUID, db: Session = Depends(get_db_session)) -> None:
    DatasetService(db).remove_dataset(id)
    Authorization().clear_assignments_for_resource(resource_id=str(id))
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
        Depends(
            Authorization.enforce(Action.DATASET__UPDATE_PROPERTIES, DatasetResolver)
        ),
    ],
)
def update_dataset(
    id: UUID, dataset: DatasetUpdate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return DatasetService(db).update_dataset(id, dataset)


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
    id: UUID, dataset: DatasetAboutUpdate, db: Session = Depends(get_db_session)
) -> None:
    return DatasetService(db).update_dataset_about(id, dataset)


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
    id: UUID, dataset: DatasetStatusUpdate, db: Session = Depends(get_db_session)
) -> None:
    return DatasetService(db).update_dataset_status(id, dataset)


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
        Depends(Authorization.enforce(Action.DATASET__CREATE_USER, DatasetResolver)),
    ],
)
def add_user_to_dataset(
    id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    return DatasetService(db).add_user_to_dataset(id, user_id)


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
        Depends(Authorization.enforce(Action.DATASET__DELETE_USER, DatasetResolver)),
    ],
)
def remove_user_from_dataset(
    id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db_session),
) -> None:
    return DatasetService(db).remove_user_from_dataset(id, user_id)


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
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
) -> None:
    return DataProductSettingService().set_value_for_product(
        setting_id, id, value, authenticated_user, db
    )
