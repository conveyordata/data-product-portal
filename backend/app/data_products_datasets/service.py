from datetime import datetime
from typing import Sequence
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.datasets.model import Dataset as DatasetModel
from app.pending_actions.schema import DataProductDatasetPendingAction
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User


class DataProductDatasetService:
    def approve_data_product_link(
        self, id: UUID, db: Session, authenticated_user: User
    ) -> None:
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if current_link.status != DecisionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already approved/denied",
            )
        current_link.status = DecisionStatus.APPROVED
        current_link.approved_by = authenticated_user
        current_link.approved_on = datetime.now(tz=pytz.utc)
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def deny_data_product_link(
        self, id: UUID, db: Session, authenticated_user: User
    ) -> None:
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if (
            current_link.status != DecisionStatus.PENDING
            and current_link.status != DecisionStatus.APPROVED
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already approved/denied",
            )
        current_link.status = DecisionStatus.DENIED
        current_link.denied_by = authenticated_user
        current_link.denied_on = datetime.now(tz=pytz.utc)
        db.commit()

    def remove_data_product_link(self, id: UUID, db: Session) -> None:
        current_link = db.get(DataProductDatasetAssociationModel, id)

        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data product link {id} not found",
            )

        db.delete(current_link)
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def get_user_pending_actions(
        self, db: Session, authenticated_user: User
    ) -> Sequence[DataProductDatasetPendingAction]:
        return (
            db.scalars(
                select(DataProductDatasetAssociationModel)
                .where(
                    DataProductDatasetAssociationModel.status == DecisionStatus.PENDING
                )
                .where(
                    DataProductDatasetAssociationModel.dataset.has(
                        DatasetModel.assignments.any(
                            DatasetRoleAssignment.user_id == authenticated_user.id
                        )
                    )
                )
                .order_by(asc(DataProductDatasetAssociationModel.requested_on))
            )
            .unique()
            .all()
        )
