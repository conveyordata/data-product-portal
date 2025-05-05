import itertools
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import desc, event, select, update
from sqlalchemy.orm import Session, joinedload

from app.data_outputs.model import DataOutput
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_memberships.model import DataProductMembership
from app.data_products.model import DataProduct
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.datasets.model import Dataset
from app.notifications.enums import NotificationTypes
from app.notifications.model import (
    DataOutputDatasetNotification,
    DataProductDatasetNotification,
    DataProductMembershipNotification,
)
from app.notifications.model import Notification as NotificationModel
from app.notifications.schema import Notification
from app.users.model import User as UserModel
from app.users.schema import User


@event.listens_for(DataProductDatasetAssociation, "before_delete")
def _backup_info_data_product_dataset(mapper, connection, target):
    stmt = (
        select(Dataset.name, DataProduct.name)
        .select_from(
            Dataset.__table__.join(
                DataProductDatasetAssociation.__table__,
                Dataset.id == DataProductDatasetAssociation.dataset_id,
            ).join(
                DataProduct.__table__,
                DataProduct.id == DataProductDatasetAssociation.data_product_id,
            )
        )
        .where(DataProductDatasetAssociation.id == target.id)
    )
    dataset_name, product_name = connection.execute(stmt).one()

    connection.execute(
        update(DataProductDatasetNotification.__table__)
        .where(DataProductDatasetNotification.data_product_dataset_id == target.id)
        .values(
            deleted_dataset_name=dataset_name,
            deleted_data_product_name=product_name,
        )
    )


@event.listens_for(DataOutputDatasetAssociation, "before_delete")
def _backup_info_data_output_dataset(mapper, connection, target):
    stmt = (
        select(Dataset.name, DataOutput.name)
        .select_from(
            Dataset.__table__.join(
                DataOutputDatasetAssociation.__table__,
                Dataset.id == DataOutputDatasetAssociation.dataset_id,
            ).join(
                DataOutput.__table__,
                DataOutput.id == DataOutputDatasetAssociation.data_output_id,
            )
        )
        .where(DataOutputDatasetAssociation.id == target.id)
    )
    dataset_name, output_name = connection.execute(stmt).one()

    connection.execute(
        update(DataOutputDatasetNotification.__table__)
        .where(DataOutputDatasetNotification.data_output_dataset_id == target.id)
        .values(
            deleted_dataset_name=dataset_name,
            deleted_data_output_name=output_name,
        )
    )


@event.listens_for(DataProductMembership, "before_delete")
def _backup_info_data_product_membership(mapper, connection, target):
    stmt = (
        select(DataProduct.name, UserModel.first_name, UserModel.last_name)
        .select_from(
            DataProductMembership.__table__.join(
                DataProduct.__table__,
                DataProduct.id == DataProductMembership.data_product_id,
            ).join(UserModel.__table__, UserModel.id == DataProductMembership.user_id)
        )
        .where(DataProductMembership.id == target.id)
    )
    product_name, first_name, last_name = connection.execute(stmt).one()

    connection.execute(
        update(DataProductMembershipNotification.__table__)
        .where(
            DataProductMembershipNotification.data_product_membership_id == target.id
        )
        .values(deleted_data_product_name=product_name)
        .values(deleted_membership_username=f"{first_name} {last_name}")
    )


class NotificationService:
    def get_user_notifications(
        self, db: Session, authenticated_user: User
    ) -> list[Notification]:
        return db.scalars(
            select(NotificationModel)
            .options(
                joinedload(NotificationModel.user),
            )
            .where(NotificationModel.user_id == authenticated_user.id)
            .order_by(desc(NotificationModel.created_on))
        ).all()

    def remove_notification(self, id: UUID, db: Session, authenticated_user: User):
        notification = db.get(
            NotificationModel,
            id,
        )
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {id} not found",
            )
        if notification.user_id != authenticated_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Notification {id} belongs to another user",
            )
        db.delete(notification)
        db.commit()

    def create_data_product_dataset_notifications(
        self, db: Session, data_product_dataset: DataProductDatasetAssociation
    ):
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_product_dataset.dataset.owners,
                    [data_product_dataset.requested_by],
                )
            )
        )
        for receiver in receivers:
            notification = DataProductDatasetNotification(
                notification_type=NotificationTypes.DataProductDatasetNotification,
                notification_origin=data_product_dataset.status,
                data_product_dataset_id=data_product_dataset.id,
                user_id=receiver,
                dataset_id=data_product_dataset.dataset_id,
                data_product_id=data_product_dataset.data_product_id,
            )
            db.add(notification)

    def create_data_output_dataset_notifications(
        self, db: Session, data_output_dataset: DataOutputDatasetAssociation
    ):
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_output_dataset.dataset.owners,
                    [data_output_dataset.requested_by],
                )
            )
        )
        for receiver in receivers:
            notification = DataOutputDatasetNotification(
                notification_type=NotificationTypes.DataOutputDatasetNotification,
                notification_origin=data_output_dataset.status,
                data_output_dataset_id=data_output_dataset.id,
                user_id=receiver,
                dataset_id=data_output_dataset.dataset_id,
                data_output_id=data_output_dataset.data_output_id,
                data_product_id=data_output_dataset.data_output.owner_id,
            )
            db.add(notification)

    def create_data_product_membership_notifications(
        self, db: Session, data_product_membership: DataProductMembership
    ):
        receivers = set(
            owner.id
            for owner in (
                itertools.chain(
                    data_product_membership.data_product.owners,
                    [data_product_membership.user],
                )
            )
        )
        for receiver in receivers:
            notification = DataProductMembershipNotification(
                notification_type=NotificationTypes.DataProductMembershipNotification,
                notification_origin=data_product_membership.status,
                data_product_membership_id=data_product_membership.id,
                user_id=receiver,
                data_product_id=data_product_membership.data_product_id,
                membership_role=data_product_membership.role,
            )
            db.add(notification)
