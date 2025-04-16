from typing import Literal, Union
from uuid import UUID

from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.notifications.enums import NotificationOrigins, NotificationTypes
from app.shared.schema import ORMModel


class NotificationBase(ORMModel):
    id: UUID
    notification_origin: NotificationOrigins


class DataProductDatasetNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataProductDatasetNotification]
    data_product_dataset_id: UUID
    data_product_dataset: DataProductDatasetAssociation


class DataOutputDatasetNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataOutputDatasetNotification]
    data_output_dataset_id: UUID
    data_output_dataset: DataOutputDatasetAssociation


class DataProductMembershipNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataProductMembershipNotification]
    data_product_membership_id: UUID
    data_product_membership: DataProductMembershipGet


Notification = Union[
    DataProductDatasetNotification,
    DataOutputDatasetNotification,
    DataProductMembershipNotification,
]
