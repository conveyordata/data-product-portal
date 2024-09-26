from datetime import datetime
from uuid import UUID

import pytz
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.aws.refresh_infrastructure_lambda import RefreshInfrastructureLambda
from app.data_products.model import ensure_data_product_exists
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.datasets.model import ensure_dataset_exists
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
        RefreshInfrastructureLambda().trigger()
        db.commit()

    def deny_data_product_link(self, id: UUID, db: Session, authenticated_user: User):
        current_link = db.get(DataProductDatasetAssociationModel, id)
        if current_link.status != DataProductDatasetLinkStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request already approved/denied",
            )
        current_link.status = DataProductDatasetLinkStatus.DENIED
        current_link.denied_by = authenticated_user
        current_link.denied_on = datetime.now(tz=pytz.utc)
        db.commit()

    def remove_data_product_link(self, id: UUID, db: Session, authenticated_user: User):
        current_link = db.get(DataProductDatasetAssociationModel, id)
        dataset = current_link.dataset
        ensure_dataset_exists(dataset.id, db)
        linked_data_product = current_link.data_product
        data_product = ensure_data_product_exists(linked_data_product.id, db)
        data_product.dataset_links.remove(current_link)
        RefreshInfrastructureLambda().trigger()
        db.commit()
