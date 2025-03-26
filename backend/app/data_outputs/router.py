from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.core.auth.auth import get_authenticated_user
from app.core.authz.actions import AuthorizationAction
from app.core.authz.authorization import Authorization
from app.data_outputs.model import DataOutput as DataOutputModel
from app.data_outputs.schema import (
    DataOutput,
    DataOutputCreate,
    DataOutputStatusUpdate,
    DataOutputUpdate,
)
from app.data_outputs.service import DataOutputService
from app.database.database import get_db_session
from app.dependencies import only_data_output_owners
from app.graph.graph import Graph
from app.users.schema import User

router = APIRouter(prefix="/data_outputs", tags=["data_outputs"])


@router.get("")
def get_data_outputs(db: Session = Depends(get_db_session)) -> list[DataOutput]:
    return DataOutputService().get_data_outputs(db)


@router.get("/{id}")
def get_data_output(id: UUID, db: Session = Depends(get_db_session)) -> DataOutput:
    return DataOutputService().get_data_output(id, db)


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
        Depends(only_data_output_owners),
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__DELETE_DATA_OUTPUT, DataOutputModel
            )
        ),
    ],
)
def remove_data_output(
    id: UUID,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
):
    return DataOutputService().remove_data_output(id, db, authenticated_user)


@router.post(
    "",
    responses={
        200: {
            "description": "DataOutput successfully created",
            "content": {
                "application/json": {
                    "example": {"id": "random id of the new data_output"}
                }
            },
        },
    },
    dependencies=[
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__CREATE_DATA_OUTPUT, DataOutputModel
            )
        )
    ],
)
def create_data_output(
    data_output: DataOutputCreate,
    db: Session = Depends(get_db_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> dict[str, UUID]:
    return DataOutputService().create_data_output(data_output, db, authenticated_user)


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
        Depends(only_data_output_owners),
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__UPDATE_DATA_OUTPUT,
                DataOutputModel,
            )
        ),
    ],
)
def update_data_output(
    id: UUID, data_output: DataOutputUpdate, db: Session = Depends(get_db_session)
):
    return DataOutputService().update_data_output(id, data_output, db)


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
        Depends(only_data_output_owners),
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__UPDATE_DATA_OUTPUT, DataOutputModel
            )
        ),
    ],
)
def update_data_output_status(
    id: UUID,
    data_output: DataOutputStatusUpdate,
    db: Session = Depends(get_db_session),
):
    return DataOutputService().update_data_output_status(id, data_output, db)


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
        Depends(only_data_output_owners),
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__REQUEST_DATA_OUTPUT_LINK,
                DataOutputModel,
            )
        ),
    ],
)
def link_dataset_to_data_output(
    id: UUID,
    dataset_id: UUID,
    background_tasks: BackgroundTasks,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    return DataOutputService().link_dataset_to_data_output(
        id, dataset_id, authenticated_user, db, background_tasks
    )


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
        Depends(only_data_output_owners),
        Depends(
            Authorization.enforce(
                AuthorizationAction.DATA_PRODUCT__REVOKE_DATASET_ACCESS, DataOutputModel
            )
        ),
    ],
)
def unlink_dataset_from_data_output(
    id: UUID,
    dataset_id: UUID,
    authenticated_user: User = Depends(get_authenticated_user),
    db: Session = Depends(get_db_session),
):
    return DataOutputService().unlink_dataset_from_data_output(
        id, dataset_id, authenticated_user, db
    )


@router.get("/{id}/graph")
def get_graph_data(
    id: UUID, db: Session = Depends(get_db_session), level: int = 3
) -> Graph:
    return DataOutputService().get_graph_data(id, level, db)
