from datetime import datetime
from typing import Sequence
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.core.authz import Action, Authorization
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.datasets.model import Dataset as DatasetModel
from app.pending_actions.schema import DataOutputDatasetPendingAction
from app.role_assignments.dataset.model import DatasetRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.users.schema import User


class DataOutputDatasetService:
    def __init__(self, db: Session):
        self.db = db

    def approve_data_output_link(
        self, id: UUID, *, actor: User
    ) -> DataOutputDatasetAssociationModel:
        current_link = self.db.get(DataOutputDatasetAssociationModel, id)
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data output link {id} not found",
            )
        if current_link.status != DecisionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request can not be already approved or denied",
            )

        current_link.status = DecisionStatus.APPROVED
        current_link.approved_by = actor
        current_link.approved_on = datetime.now(tz=pytz.utc)
        self.db.commit()
        return current_link

    def deny_data_output_link(
        self, id: UUID, *, actor: User
    ) -> DataOutputDatasetAssociationModel:
        current_link = self.db.get(DataOutputDatasetAssociationModel, id)
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data output link {id} not found",
            )

        current_link.status = DecisionStatus.DENIED
        current_link.denied_by = actor
        current_link.denied_on = datetime.now(tz=pytz.utc)
        self.db.commit()
        return current_link

    def remove_data_output_link(
        self, id: UUID, *, actor: User
    ) -> DataOutputDatasetAssociationModel:
        current_link = self.db.get(DataOutputDatasetAssociationModel, id)
        if not current_link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset data output link {id} not found",
            )

        self.db.delete(current_link)
        self.db.commit()
        return current_link

    def get_user_pending_actions(
        self, user: User
    ) -> Sequence[DataOutputDatasetPendingAction]:
        requested_associations = (
            self.db.scalars(
                select(DataOutputDatasetAssociationModel)
                .where(
                    DataOutputDatasetAssociationModel.status == DecisionStatus.PENDING,
                )
                .where(
                    DataOutputDatasetAssociationModel.dataset.has(
                        DatasetModel.assignments.any(
                            DatasetRoleAssignment.user_id == user.id
                        )
                    )
                )
                .order_by(asc(DataOutputDatasetAssociationModel.requested_on))
            )
            .unique()
            .all()
        )

        authorizer = Authorization()
        return [
            a
            for a in requested_associations
            if authorizer.has_access(
                sub=str(user.id),
                dom=str(a.dataset.domain),
                obj=str(a.dataset_id),
                act=Action.DATASET__APPROVE_DATA_OUTPUT_LINK_REQUEST,
            )
        ]
