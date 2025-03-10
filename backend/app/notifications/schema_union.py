from typing import Annotated, Union

from pydantic import Field

from app.notifications.data_output_dataset_association.schema import (
    DataOutputDatasetNotification,
)
from app.notifications.data_output_dataset_association.schema_get import (
    DataOutputDatasetNotificationGet,
)
from app.notifications.data_product_dataset_association.schema import (
    DataProductDatasetNotification,
)
from app.notifications.data_product_dataset_association.schema_get import (
    DataProductDatasetNotificationGet,
)
from app.notifications.data_product_membership.schema import (
    DataProductMembershipNotification,
)
from app.notifications.data_product_membership.schema_get import (
    DataProductMembershipNotificationGet,
)
from app.notifications.notification_types import NotificationTypes

Notifications = Union[
    DataProductMembershipNotification,
    DataProductDatasetNotification,
    DataOutputDatasetNotification,
]


NotificationsGet = Union[
    DataProductMembershipNotificationGet,
    DataProductDatasetNotificationGet,
    DataOutputDatasetNotificationGet,
]

NotificationMap = {
    NotificationTypes.DataProductMembership: DataProductMembershipNotification,
    NotificationTypes.DataProductDataset: DataProductDatasetNotification,
    NotificationTypes.DataOutputDataset: DataOutputDatasetNotification,
}

NotificationMapGet = {
    NotificationTypes.DataProductMembership: DataProductMembershipNotificationGet,
    NotificationTypes.DataProductDataset: DataProductDatasetNotificationGet,
    NotificationTypes.DataOutputDataset: DataOutputDatasetNotificationGet,
}

NotificationConfiguration = Annotated[
    Notifications,
    Field(discriminator="configuration_type"),
]

NotificationConfigurationGet = Annotated[
    NotificationsGet,
    Field(discriminator="configuration_type"),
]
