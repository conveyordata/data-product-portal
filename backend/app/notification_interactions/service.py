from uuid import UUID

from sqlalchemy import asc
from sqlalchemy.orm import Session, joinedload

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_product_memberships.enums import DataProductMembershipStatus
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
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
from app.users.schema import User


class NotificationInteractionService:
    def update_notification_interactions_for_notification(
        self, db: Session, notification_id: UUID, user_ids: list[UUID]
    ):
        """
        Clears the NotificationInteractions for the specified Notification.
        New interactions are then created for the users provided.
        db.commit() should be used after using this function.

        """
        db.query(NotificationInteraction).filter(
            NotificationInteraction.notification_id == notification_id
        ).delete(synchronize_session=False)

        for user_id in user_ids:
            new_interaction = NotificationInteraction(
                notification_id=notification_id,
                user_id=user_id,
            )
            db.add(new_interaction)

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
        data_product_dataset_notification_ids = (
            db.query(DataProductDatasetNotification.id)
            .options(joinedload(DataProductDatasetNotification.data_product_dataset))
            .filter(
                DataProductDatasetNotification.data_product_dataset.has(
                    DataProductDatasetAssociationModel.status
                    == DataProductDatasetLinkStatus.PENDING_APPROVAL
                )
            )
        )

        data_output_dataset_notification_ids = (
            db.query(DataOutputDatasetNotification.id)
            .options(joinedload(DataOutputDatasetNotification.data_output_dataset))
            .filter(
                DataOutputDatasetNotification.data_output_dataset.has(
                    DataOutputDatasetAssociationModel.status
                    == DataOutputDatasetLinkStatus.PENDING_APPROVAL
                )
            )
        )

        data_product_membership_notification_ids = (
            db.query(DataProductMembershipNotification.id)
            .options(
                joinedload(DataProductMembershipNotification.data_product_membership)
            )
            .filter(
                DataProductMembershipNotification.data_product_membership.has(
                    DataProductMembershipModel.status
                    == DataProductMembershipStatus.PENDING_APPROVAL
                )
            )
        )

        notification_ids = data_product_dataset_notification_ids.union(
            data_output_dataset_notification_ids,
            data_product_membership_notification_ids,
        )

        return (
            db.query(NotificationInteraction)
            .options(joinedload(NotificationInteraction.notification))
            .filter(NotificationInteraction.user_id == authenticated_user.id)
            .filter(NotificationInteraction.notification_id.in_(notification_ids))
            .order_by(asc(NotificationInteraction.last_seen))
        )
