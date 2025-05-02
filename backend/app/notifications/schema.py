from typing import Literal, Optional, Union
from uuid import UUID

from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.notifications.enums import NotificationTypes
from app.role_assignments.enums import DecisionStatus
from app.shared.schema import ORMModel
from app.users.schema import User


class NotificationBase(ORMModel):
    id: UUID
    notification_origin: DecisionStatus
    user_id: UUID
    user: User


class DataProductDatasetNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataProductDatasetNotification]
    deleted_data_product_identifier: Optional[str] = None
    deleted_dataset_identifier: Optional[str] = None
    data_product_dataset_id: UUID
    data_product_dataset: DataProductDatasetAssociation


class DataOutputDatasetNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataOutputDatasetNotification]
    deleted_data_output_identifier: Optional[str] = None
    deleted_dataset_identifier: Optional[str] = None
    data_output_dataset_id: UUID
    data_output_dataset: DataOutputDatasetAssociation


class DataProductMembershipNotification(NotificationBase):
    notification_type: Literal[NotificationTypes.DataProductMembershipNotification]
    deleted_data_product_identifier: Optional[str] = None
    data_product_membership_id: UUID
    data_product_membership: DataProductMembershipGet


Notification = Union[
    DataProductDatasetNotification,
    DataOutputDatasetNotification,
    DataProductMembershipNotification,
]
