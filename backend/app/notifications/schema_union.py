from typing import Annotated, Union

from pydantic import Field

from app.notifications.data_output_dataset_association.model import (
    DataOutputDatasetNotification as DataOutputDatasetNotificationModel,
)
from app.notifications.data_output_dataset_association.schema import (
    DataOutputDatasetNotification,
)
from app.notifications.data_product_dataset_association.model import (
    DataProductDatasetNotification as DataProductDatasetNotificationModel,
)
from app.notifications.data_product_dataset_association.schema import (
    DataProductDatasetNotification,
)
from app.notifications.data_product_membership.model import (
    DataProductMembershipNotification as DataProductMembershipNotificationModel,
)
from app.notifications.data_product_membership.schema import (
    DataProductMembershipNotification,
)
from app.notifications.model import Notification
from app.notifications.notification_types import NotificationTypes

Notifications = Union[
    DataProductMembershipNotification,
    DataProductDatasetNotification,
    DataOutputDatasetNotification,
]

NotificationMap = {
    NotificationTypes.DataProductMembershipNotification: (
        DataProductMembershipNotification
    ),
    NotificationTypes.DataProductDatasetNotification: (DataProductDatasetNotification),
    NotificationTypes.DataOutputDatasetNotification: (DataOutputDatasetNotification),
}

NotificationModelMap = {
    NotificationTypes.DataProductMembershipNotification: (
        DataProductMembershipNotificationModel
    ),
    NotificationTypes.DataProductDatasetNotification: (
        DataProductDatasetNotificationModel
    ),
    NotificationTypes.DataOutputDatasetNotification: (
        DataOutputDatasetNotificationModel
    ),
}

NotificationForeignKeyMap = {
    NotificationTypes.DataProductDatasetNotification: (
        Notification.__table__.c.data_product_dataset_id
    ),
    NotificationTypes.DataOutputDatasetNotification: (
        Notification.__table__.c.data_output_dataset_id
    ),
    NotificationTypes.DataProductMembershipNotification: (
        Notification.__table__.c.data_product_membership_id
    ),
}

NotificationConfiguration = Annotated[
    Notifications,
    Field(discriminator="configuration_type"),
]
