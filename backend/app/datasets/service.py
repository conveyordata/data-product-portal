from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.datasets.schema import DatasetAboutUpdate, DatasetCreateUpdate
from app.datasets.schema_get import DatasetGet, DatasetsGet
from app.tags.model import Tag as TagModel
from app.users.model import ensure_user_exists


class DatasetService:
    def get_dataset(self, id: UUID, db: Session) -> DatasetGet:
        dataset = db.get(
            DatasetModel,
            id,
            options=[
                joinedload(DatasetModel.data_product_links),
            ],
        )

        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
            )
        return dataset

    def get_datasets(self, db: Session) -> list[DatasetsGet]:
        return db.query(DatasetModel).order_by(asc(DatasetModel.name)).all()

    def get_user_datasets(self, user_id: UUID, db: Session) -> list[DatasetsGet]:
        return (
            db.query(DatasetModel)
            .options(joinedload(DatasetModel.owners))
            .join(DatasetModel.owners)
            .filter(DatasetModel.owners.any(id=user_id))
            .order_by(asc(DatasetModel.name))
            .all()
        )

    def _update_owners(
        self, dataset: DatasetCreateUpdate, db: Session, owner_ids: list[UUID] = []
    ) -> DatasetCreateUpdate:
        if not owner_ids:
            owner_ids = dataset.owners
        dataset.owners = []
        for owner in owner_ids:
            user = ensure_user_exists(owner, db)
            dataset.owners.append(user)
        return dataset

    def create_dataset(
        self, dataset: DatasetCreateUpdate, db: Session
    ) -> dict[str, UUID]:
        dataset = self._update_owners(dataset, db)
        dataset = DatasetModel(**dataset.parse_pydantic_schema())
        db.add(dataset)
        db.commit()
        RefreshInfrastructureLambda().trigger()

        return {"id": dataset.id}

    def remove_dataset(self, id: UUID, db: Session):
        dataset = db.get(
            DatasetModel,
            id,
            options=[joinedload(DatasetModel.data_product_links)],
        )
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Dataset {id} not found"
            )
        dataset.owners = []
        dataset.data_product_links = []
        dataset.tags = []
        dataset.delete()

        db.commit()
        RefreshInfrastructureLambda().trigger()

    def update_dataset(self, id: UUID, dataset: DatasetCreateUpdate, db: Session):
        current_dataset = ensure_dataset_exists(id, db)
        updated_dataset = dataset.model_dump(exclude_unset=True)

        for k, v in updated_dataset.items():
            if k == "owners":
                current_dataset = self._update_owners(current_dataset, db, v)
            elif k == "tags":
                current_dataset.tags = []
                for tag_data in v:
                    tag = TagModel(**tag_data)
                    current_dataset.tags.append(tag)
            else:
                setattr(current_dataset, k, v) if v else None
        db.commit()
        RefreshInfrastructureLambda().trigger()
        return {"id": current_dataset.id}

    def update_dataset_about(self, id: UUID, dataset: DatasetAboutUpdate, db: Session):
        current_dataset = ensure_dataset_exists(id, db)
        current_dataset.about = dataset.about
        db.commit()

    def add_user_to_dataset(self, dataset_id: UUID, user_id: UUID, db: Session):
        dataset = ensure_dataset_exists(dataset_id, db)
        user = ensure_user_exists(user_id, db)
        if user in dataset.owners:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User {user_id} is already an owner of dataset {dataset_id}",
            )

        dataset.owners.append(user)
        db.commit()
        RefreshInfrastructureLambda().trigger()

    def remove_user_from_dataset(self, dataset_id: UUID, user_id: UUID, db: Session):
        dataset = ensure_dataset_exists(dataset_id, db)
        user = ensure_user_exists(user_id, db)
        dataset.owners.remove(user)
        db.commit()
        RefreshInfrastructureLambda().trigger()
