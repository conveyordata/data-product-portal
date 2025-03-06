from typing import Literal
from uuid import UUID

from app.notifications.data_product_membership.model import (
    DataProductMembershipNotification as DataProductMembershipNotificationModel,
)
from app.notifications.notification_types import NotificationTypes
from app.notifications.schema_base import BaseNotificationConfiguration


class DataProductMembershipNotification(BaseNotificationConfiguration):
    data_product_membership_id: UUID
    configuration_type: Literal[NotificationTypes.DataProductMembership]

    class Meta:
        orm_model = DataProductMembershipNotificationModel
