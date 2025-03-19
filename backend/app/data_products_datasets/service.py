from datetime import datetime
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products.model import ensure_data_product_exists
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.datasets.model import Dataset as DatasetModel
from app.datasets.model import ensure_dataset_exists
from app.notification_interactions.service import NotificationInteractionService
from app.notifications.notification_types import NotificationTypes
from app.users.model import User as UserModel
from app.users.schema import User


class DataProductDatasetService:
    def approve_data_product_link(
        self, id: UUID, db: Session, authenticated_user: User
    ):
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if current_link.status != DataProductDatasetLinkStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already approved/denied",
            )
        current_link.status = DataProductDatasetLinkStatus.APPROVED
        current_link.approved_by = authenticated_user
        current_link.approved_on = datetime.now(tz=pytz.utc)

        NotificationInteractionService().update_interactions_by_reference(
            db,
            current_link.id,
            NotificationTypes.DataProductDataset,
            [current_link.requested_by_id],
        )

        RefreshInfrastructureLambda().trigger()
        db.commit()

    def deny_data_product_link(self, id: UUID, db: Session, authenticated_user: User):
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if (
            current_link.status != DataProductDatasetLinkStatus.PENDING_APPROVAL
            and current_link.status != DataProductDatasetLinkStatus.APPROVED
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already approved/denied",
            )
        current_link.status = DataProductDatasetLinkStatus.DENIED
        current_link.denied_by = authenticated_user
        current_link.denied_on = datetime.now(tz=pytz.utc)

        NotificationInteractionService().update_interactions_by_reference(
            db,
            current_link.id,
            NotificationTypes.DataProductDataset,
            [current_link.requested_by_id],
        )

        db.commit()

    def remove_data_product_link(self, id: UUID, db: Session, authenticated_user: User):
        current_link = db.get(DataProductDatasetAssociationModel, id)
        dataset = current_link.dataset
        ensure_dataset_exists(dataset.id, db)
        linked_data_product = current_link.data_product
        data_product = ensure_data_product_exists(linked_data_product.id, db)
        NotificationInteractionService().remove_notification_relations(
            db, current_link.id, NotificationTypes.DataProductDataset
        )
        db.refresh(current_link)
        data_product.dataset_links.remove(current_link)
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def get_user_pending_actions(
        self, db: Session, authenticated_user: User
    ) -> list[DataProductDatasetAssociation]:
        return (
            db.query(DataProductDatasetAssociationModel)
            .options(
                joinedload(DataProductDatasetAssociationModel.dataset).joinedload(
                    DatasetModel.owners
                ),
                joinedload(DataProductDatasetAssociationModel.data_product),
                joinedload(DataProductDatasetAssociationModel.requested_by),
            )
            .filter(
                DataProductDatasetAssociationModel.status
                == DataProductDatasetLinkStatus.PENDING_APPROVAL
            )
            .filter(
                DataProductDatasetAssociationModel.dataset.has(
                    DatasetModel.owners.any(UserModel.id == authenticated_user.id)
                )
            )
            .order_by(asc(DataProductDatasetAssociationModel.requested_on))
            .all()
        )

    def get_pending_action_ids(self, db: Session, dataset_id: UUID) -> list[UUID]:
        return [
            row.id
            for row in db.query(DataProductDatasetAssociationModel.id)
            .filter(
                DataProductDatasetAssociationModel.status
                == DataProductDatasetLinkStatus.PENDING_APPROVAL
            )
            .filter(DataProductDatasetAssociationModel.dataset_id == dataset_id)
            .all()
        ]
