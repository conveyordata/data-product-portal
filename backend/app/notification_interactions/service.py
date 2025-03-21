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
from app.data_products.model import ensure_data_product_exists
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.datasets.model import ensure_dataset_exists
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
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_union import (
    NotificationForeignKeyMap,
    NotificationModelMap,
)
from app.notifications.service import NotificationService
from app.users.schema import User


class NotificationInteractionService:
    def reset_interactions_for_notification(
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

    def update_interactions_by_reference(
        self,
        db: Session,
        reference_id: UUID,
        notification_type: NotificationTypes,
        user_ids: list[UUID],
    ):
        """
        Clears the NotificationInteractions for the specified Notification.
        New interactions are then created for the users provided.
        db.commit() should be used after using this function.

        """
        notification_cls = NotificationModelMap[notification_type]
        key_attribute = NotificationForeignKeyMap.get(notification_type)
        notification_id = (
            db.query(notification_cls.id).filter(key_attribute == reference_id).scalar()
        )
        if notification_id:
            self.reset_interactions_for_notification(db, notification_id, user_ids)

    def remove_notification_relations(
        self, db: Session, reference_id: UUID, notification_type: NotificationTypes
    ):
        """
        Removes all notification info related to the id.
        db.commit() should be used after using this function.

        """
        notification_cls = NotificationModelMap[notification_type]
        key_attribute = NotificationForeignKeyMap.get(notification_type)
        notifications_to_delete = (
            db.query(notification_cls).filter(key_attribute == reference_id).all()
        )
        if notifications_to_delete:
            db.query(NotificationInteraction).filter(
                NotificationInteraction.notification_id.in_(
                    [n.id for n in notifications_to_delete]
                )
            ).delete(synchronize_session=False)

            db.query(notification_cls).filter(key_attribute == reference_id).delete(
                synchronize_session=False
            )
            db.flush()

    def redirect_pending_requests(
        self,
        db: Session,
        reference_parent_id: UUID,
        notification_type: NotificationTypes,
        updated_owner_ids: list[UUID] = [],
    ):
        """
        Ensures pending requests are received by the correct owners.
        db.commit() should be used after using this function.

        """
        if not updated_owner_ids:
            db.flush()
            notification_owner_ids = {
                NotificationTypes.DataProductDataset: lambda db, ref_id: [
                    owner.id for owner in ensure_dataset_exists(ref_id, db).owners
                ],
                NotificationTypes.DataOutputDataset: lambda db, ref_id: [
                    owner.id for owner in ensure_dataset_exists(ref_id, db).owners
                ],
                NotificationTypes.DataProductMembership: lambda db, ref_id: [
                    membership.user_id
                    for membership in ensure_data_product_exists(ref_id, db).memberships
                ],
            }
            if notification_type in notification_owner_ids:
                updated_owner_ids = notification_owner_ids[notification_type](
                    db, reference_parent_id
                )
            else:
                raise ValueError(f"Unsupported notification type: {notification_type}")

        pending_notifications_ids = (
            NotificationService().get_pending_notifications_by_reference(
                db, reference_parent_id, notification_type
            )
        )
        for notification_id in pending_notifications_ids:
            NotificationInteractionService().reset_interactions_for_notification(
                db, notification_id, updated_owner_ids
            )

    def create_notification_relations(
        self,
        db: Session,
        reference_id: UUID,
        receiving_ids: list[UUID],
        notification_type: NotificationTypes,
    ):
        """
        Ensures pending requests are received by the correct owners.
        db.commit() should be used after using this function.

        """
        notification = NotificationService().initiate_notification_by_reference(
            db, reference_id, notification_type
        )
        self.reset_interactions_for_notification(db, notification.id, receiving_ids)

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
