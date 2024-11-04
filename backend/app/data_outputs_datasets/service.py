from datetime import datetime
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_outputs.model import ensure_data_output_exists
from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.datasets.model import ensure_dataset_exists
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
        if current_link.status != DataOutputDatasetLinkStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request can not be already approved or denied",
            )
        current_link.status = DataOutputDatasetLinkStatus.APPROVED
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
        current_link.status = DataOutputDatasetLinkStatus.DENIED
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
        ensure_dataset_exists(dataset.id, db)
        if authenticated_user not in dataset.owners and not authenticated_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only dataset owners can execute this action",
            )
        linked_data_output = current_link.data_output
        data_output = ensure_data_output_exists(linked_data_output.id, db)
        data_output.dataset_links.remove(current_link)
        RefreshInfrastructureLambda().trigger()
        db.commit()
