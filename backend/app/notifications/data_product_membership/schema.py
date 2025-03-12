from typing import Literal
from uuid import UUID

from app.data_product_memberships.schema import DataProductMembership
from app.notifications.data_product_membership.model import (
    DataProductMembershipNotification as DataProductMembershipNotificationModel,
)
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema import Notification


class DataProductMembershipNotification(Notification):
    data_product_membership_id: UUID
    data_product_membership: DataProductMembership
    configuration_type: Literal[NotificationTypes.DataProductMembership]

    class Meta:
        orm_model = DataProductMembershipNotificationModel
