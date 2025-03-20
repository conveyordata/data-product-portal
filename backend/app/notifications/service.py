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
from app.notifications.data_output_dataset_association.model import (
    DataOutputDatasetNotification,
)
from app.notifications.data_product_dataset_association.model import (
    DataProductDatasetNotification,
)
from app.notifications.data_product_membership.model import (
    DataProductMembershipNotification,
)
from app.notifications.notification_types import NotificationTypes


class NotificationService:

    def get_data_product_membership_notification_pending_ids(
        self, db: Session, data_product_id: UUID
    ) -> list[UUID]:
        return [
            notification.id
            for notification in db.query(DataProductMembershipNotification)
            .join(
                DataProductMembership,
                DataProductMembership.id
                == DataProductMembershipNotification.data_product_membership_id,
            )
            .filter(
                DataProductMembership.status
                == DataProductMembershipStatus.PENDING_APPROVAL
            )
            .filter(DataProductMembership.data_product_id == data_product_id)
            .all()
        ]

    def get_data_output_dataset_notification_pending_ids(
        self, db: Session, dataset_id: UUID
    ) -> list[UUID]:
        return [
            notification.id
            for notification in db.query(DataOutputDatasetNotification)
            .join(
                DataOutputDatasetAssociation,
                DataOutputDatasetAssociation.id
                == DataOutputDatasetNotification.data_output_dataset_id,
            )
            .filter(
                DataOutputDatasetAssociation.status
                == DataOutputDatasetLinkStatus.PENDING_APPROVAL
            )
            .filter(DataOutputDatasetAssociation.dataset_id == dataset_id)
            .all()
        ]

    def get_data_product_dataset_notification_pending_ids(
        self, db: Session, dataset_id: UUID
    ) -> list[UUID]:
        return [
            notification.id
            for notification in db.query(DataProductDatasetNotification)
            .join(
                DataProductDatasetAssociation,
                DataProductDatasetAssociation.id
                == DataProductDatasetNotification.data_product_dataset_id,
            )
            .filter(
                DataProductDatasetAssociation.status
                == DataProductDatasetLinkStatus.PENDING_APPROVAL
            )
            .filter(DataProductDatasetAssociation.dataset_id == dataset_id)
            .all()
        ]

    def get_pending_notifications_by_reference(
        self,
        db: Session,
        reference_parent_id: UUID,
        notification_type: NotificationTypes,
    ) -> list[UUID]:
        notification_function_map = {
            NotificationTypes.DataProductDataset: self.get_data_product_dataset_notification_pending_ids,
            NotificationTypes.DataOutputDataset: self.get_data_output_dataset_notification_pending_ids,
            NotificationTypes.DataProductMembership: self.get_data_product_membership_notification_pending_ids,
        }
        if notification_type in notification_function_map:
            return notification_function_map[notification_type](db, reference_parent_id)
        else:
            raise ValueError(f"Unsupported notification type: {notification_type}")
