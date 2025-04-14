from typing import Literal, Union
from uuid import UUID

from app.data_outputs_datasets.enums import DataOutputDatasetLinkStatus
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_memberships.enums import DataProductMembershipStatus
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_products_datasets.enums import DataProductDatasetLinkStatus
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.notifications.notification_types import NotificationTypes
from app.shared.schema import ORMModel


class NotificationBase(ORMModel):
    id: UUID


class DataProductDatasetNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataProductDatasetNotification]
    notification_origin: DataProductDatasetLinkStatus
    data_product_dataset_id: UUID
    data_product_dataset: DataProductDatasetAssociation


class DataOutputDatasetNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataOutputDatasetNotification]
    notification_origin: DataOutputDatasetLinkStatus
    data_output_dataset_id: UUID
    data_output_dataset: DataOutputDatasetAssociation


class DataProductMembershipNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataProductMembershipNotification]
    notification_origin: DataProductMembershipStatus
    data_product_membership_id: UUID
    data_product_membership: DataProductMembershipGet


Notification = Union[
    DataProductDatasetNotification,
    DataOutputDatasetNotification,
    DataProductMembershipNotification,
]
