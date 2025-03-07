from typing import Annotated, Union

from pydantic import Field

from app.notifications.data_output_dataset_association.schema import (
    DataOutputDatasetNotification,
)
from app.notifications.data_product_dataset_association.schema import (
    DataProductDatasetNotification,
)
from app.notifications.data_product_membership.schema import (
    DataProductMembershipNotification,
)
from app.notifications.notification_types import NotificationTypes

Notifications = Union[
    DataProductMembershipNotification,
    DataProductDatasetNotification,
    DataOutputDatasetNotification,
]

NotificationMap = {
    NotificationTypes.DataProductMembership: DataProductMembershipNotification,
    NotificationTypes.DataProductDataset: DataProductDatasetNotification,
    NotificationTypes.DataOutputDataset: DataOutputDatasetNotification,
}

NotificationConfiguration = Annotated[
    Notifications,
    Field(discriminator="configuration_type"),
]
