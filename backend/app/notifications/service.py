from uuid import UUID

from sqlalchemy import select
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
from app.notifications.model import Notification
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_union import (
    NotificationForeignKeyMap,
    NotificationModelMap,
)


class NotificationService:

    def get_data_product_membership_notification_pending_ids(
        self, db: Session, data_product_id: UUID
    ) -> list[UUID]:
        return db.scalars(
            select(DataProductMembershipNotification.id)
            .join(
                DataProductMembership,
                DataProductMembership.id
                == DataProductMembershipNotification.data_product_membership_id,
            )
            .where(
                DataProductMembership.status
                == DataProductMembershipStatus.PENDING_APPROVAL,
                DataProductMembership.data_product_id == data_product_id,
            )
        ).all()

    def get_data_output_dataset_notification_pending_ids(
        self, db: Session, dataset_id: UUID
    ) -> list[UUID]:
        return db.scalars(
            select(DataOutputDatasetNotification.id)
            .join(
                DataOutputDatasetAssociation,
                DataOutputDatasetAssociation.id
                == DataOutputDatasetNotification.data_output_dataset_id,
            )
            .where(
                DataOutputDatasetAssociation.status
                == DataOutputDatasetLinkStatus.PENDING_APPROVAL,
                DataOutputDatasetAssociation.dataset_id == dataset_id,
            )
        ).all()

    def get_data_product_dataset_notification_pending_ids(
        self, db: Session, dataset_id: UUID
    ) -> list[UUID]:
        return db.scalars(
            select(DataProductDatasetNotification.id)
            .join(
                DataProductDatasetAssociation,
                DataProductDatasetAssociation.id
                == DataProductDatasetNotification.data_product_dataset_id,
            )
            .where(
                DataProductDatasetAssociation.status
                == DataProductDatasetLinkStatus.PENDING_APPROVAL,
                DataProductDatasetAssociation.dataset_id == dataset_id,
            )
        ).all()

    def get_pending_notifications_by_reference(
        self,
        db: Session,
        reference_parent_id: UUID,
        notification_type: NotificationTypes,
    ) -> list[UUID]:
        """
        Receives the UUID's for pending notifications.
        'reference_parent_id' is the id of the parent that is:
        -> linked to notification referenced object
        -> linked to the notification.
        db.commit() should be used after using this function.

        """
        notification_function_map = {
            NotificationTypes.DataProductDatasetNotification: (
                self.get_data_product_dataset_notification_pending_ids
            ),
            NotificationTypes.DataOutputDatasetNotification: (
                self.get_data_output_dataset_notification_pending_ids
            ),
            NotificationTypes.DataProductMembershipNotification: (
                self.get_data_product_membership_notification_pending_ids
            ),
        }
        if notification_type in notification_function_map:
            return notification_function_map[notification_type](db, reference_parent_id)
        else:
            raise ValueError(f"Unsupported notification type: {notification_type}")

    def initiate_notification_by_reference(
        self,
        db: Session,
        reference_id: UUID,
        notification_type: NotificationTypes,
    ) -> Notification:
        """
        Creates a Notification object for NotificationInteraction
        objects to attach to.
        db.commit() should be used after using this function.

        """
        notification_cls = NotificationModelMap[notification_type]
        key_attribute = NotificationForeignKeyMap[notification_type]
        notification = notification_cls(**{key_attribute: reference_id})
        db.add(notification)
        db.flush()
        db.refresh(notification)
        return notification
