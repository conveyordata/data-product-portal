from datetime import datetime
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.data_products_datasets.schema_response import DataProductDatasetAssociationsGet
from app.datasets.model import Dataset as Dataset
from app.role_assignments.enums import DecisionStatus
from app.users.model import User as UserModel
from app.users.schema import User


class DataProductDatasetService:
    def approve_data_product_link(
        self, id: UUID, db: Session, authenticated_user: User
    ):
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

    def deny_data_product_link(self, id: UUID, db: Session, authenticated_user: User):
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

    def remove_data_product_link(self, id: UUID, db: Session, authenticated_user: User):
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
    ) -> list[DataProductDatasetAssociationsGet]:
        return (
            db.query(DataProductDatasetAssociationModel)
            .options(
                joinedload(DataProductDatasetAssociationModel.dataset).joinedload(
                    Dataset.owners
                ),
                joinedload(DataProductDatasetAssociationModel.data_product),
                joinedload(DataProductDatasetAssociationModel.requested_by),
            )
            .filter(DataProductDatasetAssociationModel.status == DecisionStatus.PENDING)
            .filter(
                DataProductDatasetAssociationModel.dataset.has(
                    Dataset.owners.any(UserModel.id == authenticated_user.id)
                )
            )
            .order_by(asc(DataProductDatasetAssociationModel.requested_on))
            .all()
        )
