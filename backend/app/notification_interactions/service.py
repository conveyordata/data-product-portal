from typing import Iterable
from uuid import UUID

from sqlalchemy import and_, asc, delete, select
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
from app.notifications.model import Notification
from app.notifications.notification_types import NotificationTypes
from app.notifications.service import NotificationService
from app.users.schema import User


class NotificationInteractionService:
    def reset_interactions_for_notification(
        self, db: Session, notification_id: UUID, user_ids: Iterable[UUID]
    ):
        """
        Clears the NotificationInteractions for the specified Notification.
        New interactions are then created for the users provided.
        db.commit() should be used after using this function.

        """
        db.execute(
            delete(NotificationInteraction).where(
                NotificationInteraction.notification_id == notification_id
            )
        )
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
        user_ids: Iterable[UUID],
    ):
        """
        Clears the NotificationInteractions for the specified Notification.
        New interactions are then created for the users provided.
        db.commit() should be used after using this function.

        """
        notification_id = db.scalars(
            select(Notification.id).where(
                and_(
                    Notification.reference_id == reference_id,
                    Notification.configuration_type == notification_type,
                )
            )
        ).one_or_none()
        if notification_id:
            self.reset_interactions_for_notification(db, notification_id, user_ids)

    def remove_notification_relations(
        self, db: Session, reference_id: UUID, notification_type: NotificationTypes
    ):
        """
        Removes all notification info related to the id.
        db.commit() should be used after using this function.

        """
        notification_id = db.scalars(
            select(Notification.id).where(
                and_(
                    Notification.reference_id == reference_id,
                    Notification.configuration_type == notification_type,
                )
            )
        ).one_or_none()
        if notification_id:
            db.execute(
                delete(NotificationInteraction).where(
                    NotificationInteraction.notification_id == notification_id
                )
            )
            db.execute(
                delete(Notification).where(
                    and_(
                        Notification.reference_id == reference_id,
                        Notification.configuration_type == notification_type,
                    )
                )
            )
            db.flush()

    def get_owner_ids_via_reference_parent_id(
        self,
        db: Session,
        reference_parent_id: UUID,
        notification_type: NotificationTypes,
    ) -> list[UUID]:
        notification_owner_ids = {
            NotificationTypes.DataProductDatasetNotification: lambda db, ref_id: [
                owner.id for owner in ensure_dataset_exists(ref_id, db).owners
            ],
            NotificationTypes.DataOutputDatasetNotification: lambda db, ref_id: [
                owner.id for owner in ensure_dataset_exists(ref_id, db).owners
            ],
            NotificationTypes.DataProductMembershipNotification: lambda db, ref_id: [
                membership.user_id
                for membership in ensure_data_product_exists(ref_id, db).memberships
            ],
        }
        if notification_type in notification_owner_ids:
            return notification_owner_ids[notification_type](db, reference_parent_id)
        else:
            raise ValueError(f"Unsupported notification type: {notification_type}")

    def redirect_pending_requests(
        self,
        db: Session,
        reference_parent_id: UUID,
        notification_type: NotificationTypes,
        updated_owner_ids: Iterable[UUID] = [],
    ):
        """
        Called from parent of a notification referenced object
        Ensures pending requests are received by the correct owners.
        db.commit() should be used after using this function.

        """
        if not updated_owner_ids:
            db.flush()
            updated_owner_ids = self.get_owner_ids_via_reference_parent_id(
                db, reference_parent_id, notification_type
            )

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
        notification_type: NotificationTypes,
        receiving_ids: Iterable[UUID] = [],
    ):
        """
        Called from notification referenced object
        Ensures pending requests are received by the correct owners.
        db.commit() should be used after using this function.

        """
        if not receiving_ids:
            db.flush()
            notification_owner_ids = {
                NotificationTypes.DataProductDatasetNotification: (
                    lambda db, ref_id: self.get_owner_ids_via_reference_parent_id(
                        db,
                        db.scalars(
                            select(DataProductDatasetAssociationModel.dataset_id).where(
                                DataProductDatasetAssociationModel.id == ref_id
                            )
                        ).one_or_none(),
                        notification_type,
                    )
                ),
                NotificationTypes.DataOutputDatasetNotification: (
                    lambda db, ref_id: self.get_owner_ids_via_reference_parent_id(
                        db,
                        db.scalars(
                            select(DataOutputDatasetAssociationModel.dataset_id).where(
                                DataOutputDatasetAssociationModel.id == ref_id
                            )
                        ).one_or_none(),
                        notification_type,
                    )
                ),
                NotificationTypes.DataProductMembershipNotification: (
                    lambda db, ref_id: self.get_owner_ids_via_reference_parent_id(
                        db,
                        db.scalars(
                            select(DataProductMembershipModel.data_product_id).where(
                                DataProductMembershipModel.id == ref_id
                            )
                        ).one_or_none(),
                        notification_type,
                    )
                ),
            }
            if notification_type in notification_owner_ids:
                receiving_ids = notification_owner_ids[notification_type](
                    db, reference_id
                )
            else:
                raise ValueError(f"Unsupported notification type: {notification_type}")

        notification = NotificationService().initiate_notification_by_reference(
            db, reference_id, notification_type
        )
        self.reset_interactions_for_notification(db, notification.id, receiving_ids)

    def get_user_notification_interactions(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationInteractionGet]:
        return db.scalars(
            select(NotificationInteraction)
            .options(
                joinedload(NotificationInteraction.notification),
                joinedload(NotificationInteraction.user),
            )
            .where(NotificationInteraction.user_id == authenticated_user.id)
            .order_by(asc(NotificationInteraction.last_seen))
        ).all()

    def get_user_action_notification_interactions(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationInteractionGet]:
        data_product_dataset_notification_ids = db.scalars(
            select(Notification.id)
            .join(
                DataProductDatasetAssociationModel,
                DataProductDatasetAssociationModel.id == Notification.reference_id,
            )
            .where(
                and_(
                    Notification.configuration_type
                    == NotificationTypes.DataProductDatasetNotification,
                    DataProductDatasetAssociationModel.status
                    == DataProductDatasetLinkStatus.PENDING_APPROVAL,
                )
            )
        ).all()

        data_output_dataset_notification_ids = db.scalars(
            select(Notification.id)
            .join(
                DataOutputDatasetAssociationModel,
                DataOutputDatasetAssociationModel.id == Notification.reference_id,
            )
            .where(
                and_(
                    Notification.configuration_type
                    == NotificationTypes.DataOutputDatasetNotification,
                    DataOutputDatasetAssociationModel.status
                    == DataOutputDatasetLinkStatus.PENDING_APPROVAL,
                )
            )
        ).all()

        data_product_membership_notification_ids = db.scalars(
            select(Notification.id)
            .join(
                DataProductMembershipModel,
                DataProductMembershipModel.id == Notification.reference_id,
            )
            .where(
                and_(
                    Notification.configuration_type
                    == NotificationTypes.DataProductMembershipNotification,
                    DataProductMembershipModel.status
                    == DataProductMembershipStatus.PENDING_APPROVAL,
                )
            )
        ).all()

        notification_ids = set(data_product_dataset_notification_ids).union(
            data_output_dataset_notification_ids,
            data_product_membership_notification_ids,
        )

        return db.scalars(
            select(NotificationInteraction)
            .options(joinedload(NotificationInteraction.notification))
            .where(
                NotificationInteraction.user_id == authenticated_user.id,
                NotificationInteraction.notification_id.in_(notification_ids),
            )
            .order_by(asc(NotificationInteraction.last_seen))
        ).all()

    def get_user_confirmation_notification_interactions(
        self, db: Session, authenticated_user: User
    ) -> list[NotificationInteractionGet]:
        data_product_dataset_notification_ids = db.scalars(
            select(Notification.id)
            .join(
                DataProductDatasetAssociationModel,
                DataProductDatasetAssociationModel.id == Notification.reference_id,
            )
            .where(
                and_(
                    Notification.configuration_type
                    == NotificationTypes.DataProductDatasetNotification,
                    DataProductDatasetAssociationModel.status
                    != DataProductDatasetLinkStatus.PENDING_APPROVAL,
                )
            )
        ).all()

        data_output_dataset_notification_ids = db.scalars(
            select(Notification.id)
            .join(
                DataOutputDatasetAssociationModel,
                DataOutputDatasetAssociationModel.id == Notification.reference_id,
            )
            .where(
                and_(
                    Notification.configuration_type
                    == NotificationTypes.DataOutputDatasetNotification,
                    DataOutputDatasetAssociationModel.status
                    != DataOutputDatasetLinkStatus.PENDING_APPROVAL,
                )
            )
        ).all()

        data_product_membership_notification_ids = db.scalars(
            select(Notification.id)
            .join(
                DataProductMembershipModel,
                DataProductMembershipModel.id == Notification.reference_id,
            )
            .where(
                and_(
                    Notification.configuration_type
                    == NotificationTypes.DataProductMembershipNotification,
                    DataProductMembershipModel.status
                    != DataProductMembershipStatus.PENDING_APPROVAL,
                )
            )
        ).all()

        notification_ids = set(data_product_dataset_notification_ids).union(
            data_output_dataset_notification_ids,
            data_product_membership_notification_ids,
        )

        return db.scalars(
            select(NotificationInteraction)
            .options(joinedload(NotificationInteraction.notification))
            .where(
                NotificationInteraction.user_id == authenticated_user.id,
                NotificationInteraction.notification_id.in_(notification_ids),
            )
            .order_by(asc(NotificationInteraction.last_seen))
        ).all()
