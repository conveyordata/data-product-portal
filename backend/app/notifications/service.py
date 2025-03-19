from uuid import UUID

from sqlalchemy.orm import Session

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
)
from app.data_product_memberships.model import DataProductMembership
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import DataProductDatasetAssociation


class NotificationService:

    def get_data_product_membership_pending_ids(
        self, db: Session, data_product_id: UUID
    ) -> list[UUID]:
        return [
            row.id
            for row in db.query(DataProductMembership.id)
            .filter(
                DataProductMembership.status
                == DataProductMembershipStatus.PENDING_APPROVAL
            )
            .filter(DataProductMembership.data_product_id == data_product_id)
            .all()
        ]

    def get_data_output_dataset_pending_ids(
        self, db: Session, dataset_id: UUID
    ) -> list[UUID]:
        return [
            row.id
            for row in db.query(DataOutputDatasetAssociation.id)
            .filter(
                DataOutputDatasetAssociation.status
                == DataOutputDatasetLinkStatus.PENDING_APPROVAL
            )
            .filter(DataOutputDatasetAssociation.dataset_id == dataset_id)
            .all()
        ]

    def get_data_product_dataset_pending_ids(
        self, db: Session, dataset_id: UUID
    ) -> list[UUID]:
        return [
            row.id
            for row in db.query(DataProductDatasetAssociation.id)
            .filter(
                DataProductDatasetAssociation.status
                == DataProductDatasetLinkStatus.PENDING_APPROVAL
            )
            .filter(DataProductDatasetAssociation.dataset_id == dataset_id)
            .all()
        ]
