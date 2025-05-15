from datetime import datetime
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_outputs_datasets.schema_response import DataOutputDatasetAssociationsGet
from app.datasets.model import Dataset as Dataset
from app.role_assignments.enums import DecisionStatus
from app.users.model import User as UserModel
from app.users.schema import User


class DataOutputDatasetService:
    def approve_data_output_link(self, id: UUID, db: Session, authenticated_user: User):
        current_link = db.get(DataOutputDatasetAssociationModel, id)
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data output link {id} not found",
            )
        if (
            authenticated_user not in current_link.dataset.owners
            and not authenticated_user.is_admin
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only dataset owners can execute this action",
            )
        if current_link.status != DecisionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request can not be already approved or denied",
            )
        current_link.status = DecisionStatus.APPROVED
        current_link.approved_by = authenticated_user
        current_link.approved_on = datetime.now(tz=pytz.utc)
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def deny_data_output_link(self, id: UUID, db: Session, authenticated_user: User):
        current_link = db.get(DataOutputDatasetAssociationModel, id)
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data output link {id} not found",
            )
        if (
            authenticated_user not in current_link.dataset.owners
            and not authenticated_user.is_admin
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only dataset owners can execute this action",
            )
        current_link.status = DecisionStatus.DENIED
        current_link.denied_by = authenticated_user
        current_link.denied_on = datetime.now(tz=pytz.utc)
        db.commit()

    def remove_data_output_link(self, id: UUID, db: Session, authenticated_user: User):
        current_link = db.get(DataOutputDatasetAssociationModel, id)

        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data output link {id} not found",
            )

        dataset = current_link.dataset
        if authenticated_user not in dataset.owners and not authenticated_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only dataset owners can execute this action",
            )

        db.delete(current_link)
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def get_user_pending_actions(
        self, db: Session, authenticated_user: User
    ) -> list[DataOutputDatasetAssociationsGet]:
        return (
            db.scalars(
                select(DataOutputDatasetAssociationModel)
                .filter(
                    DataOutputDatasetAssociationModel.status == DecisionStatus.PENDING,
                )
                .filter(
                    DataOutputDatasetAssociationModel.dataset.has(
                        Dataset.owners.any(UserModel.id == authenticated_user.id)
                    )
                )
                .order_by(asc(DataOutputDatasetAssociationModel.requested_on))
            )
            .unique()
            .all()
        )
