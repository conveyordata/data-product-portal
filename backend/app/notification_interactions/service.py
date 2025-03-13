from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import and_, or_

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_product_memberships.enums import DataProductMembershipStatus
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.notification_interactions.model import NotificationInteraction
from app.notification_interactions.schema_get import NotificationInteractionGet
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
from app.users.schema import User


class NotificationInteractionService:
    def get_user_notification_interactions(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationInteractionGet]:
        return (
            db.query(NotificationInteraction)
            .options(
                joinedload(NotificationInteraction.notification),
                joinedload(NotificationInteraction.user),
            )
            .filter(NotificationInteraction.user_id == authenticated_user.id)
            .order_by(asc(NotificationInteraction.last_seen))
            .all()
        )

    def get_user_action_notification_interactions(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationInteractionGet]:
        query = (
            db.query(NotificationInteraction)
            .options(
                joinedload(NotificationInteraction.notification)
            )  # Loads notifications efficiently
            .filter(NotificationInteraction.user_id == authenticated_user.id)
            .order_by(asc(NotificationInteraction.last_seen))
        )

        # Define filtering conditions for polymorphic notifications
        conditions = [
            and_(
                Notification.configuration_type == NotificationTypes.DataProductDataset,
                Notification.id.in_(
                    db.query(DataProductDatasetNotification.id)
                    .filter(
                        DataProductDatasetNotification.data_product_dataset.has(
                            status=DataProductDatasetLinkStatus.PENDING_APPROVAL
                        )
                    )
                    .subquery()
                ),
            ),
            and_(
                Notification.configuration_type == NotificationTypes.DataOutputDataset,
                Notification.id.in_(
                    db.query(DataOutputDatasetNotification.id)
                    .filter(
                        DataOutputDatasetNotification.data_output_dataset.has(
                            status=DataOutputDatasetLinkStatus.PENDING_APPROVAL
                        )
                    )
                    .subquery()
                ),
            ),
            and_(
                Notification.configuration_type
                == NotificationTypes.DataProductMembership,
                Notification.id.in_(
                    db.query(DataProductMembershipNotification.id)
                    .filter(
                        DataProductMembershipNotification.data_product_membership.has(
                            status=DataProductMembershipStatus.PENDING_APPROVAL
                        )
                    )
                    .subquery()
                ),
            ),
        ]

        query = query.filter(or_(*conditions))

        return query.all()
