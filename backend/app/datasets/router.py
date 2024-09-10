from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.datasets.schema import DatasetAboutUpdate, DatasetCreateUpdate
from app.datasets.schema_get import DatasetGet, DatasetsGet
from app.datasets.service import DatasetService
from app.dependencies import only_dataset_owners

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def get_datasets(db: Session = Depends(get_db_session)) -> list[DatasetsGet]:
    return DatasetService().get_datasets(db)


@router.get("/{id}")
def get_dataset(id: UUID, db: Session = Depends(get_db_session)) -> DatasetGet:
    return DatasetService().get_dataset(id, db)


@router.get("/user/{user_id}")
def get_user_datasets(
    user_id: UUID, db: Session = Depends(get_db_session)
) -> list[DatasetsGet]:
    return DatasetService().get_user_datasets(user_id, db)


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
)
def create_dataset(
    dataset: DatasetCreateUpdate, db: Session = Depends(get_db_session)
) -> dict[str, UUID]:
    return DatasetService().create_dataset(dataset, db)


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
    dependencies=[Depends(only_dataset_owners)],
)
def remove_dataset(id: UUID, db: Session = Depends(get_db_session)):
    return DatasetService().remove_dataset(id, db)


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
    dependencies=[Depends(only_dataset_owners)],
)
def update_dataset(
    id: UUID, dataset: DatasetCreateUpdate, db: Session = Depends(get_db_session)
):
    return DatasetService().update_dataset(id, dataset, db)


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
    dependencies=[Depends(only_dataset_owners)],
)
def update_dataset_about(
    id: UUID, dataset: DatasetAboutUpdate, db: Session = Depends(get_db_session)
):
    return DatasetService().update_dataset_about(id, dataset, db)


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
    dependencies=[Depends(only_dataset_owners)],
)
def add_user_to_dataset(
    id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db_session),
):
    return DatasetService().add_user_to_dataset(id, user_id, db)


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
    dependencies=[Depends(only_dataset_owners)],
)
def remove_user_from_dataset(
    id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db_session),
):
    return DatasetService().remove_user_from_dataset(id, user_id, db)
