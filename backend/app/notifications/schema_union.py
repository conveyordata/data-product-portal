from typing import Annotated, Union

from pydantic import Field

from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.notifications.notification_types import NotificationTypes

Notifications = Union[
    DataProductMembershipGet,
    DataProductDatasetAssociation,
    DataOutputDatasetAssociation,
]

NotificationMap = {
    NotificationTypes.DataProductMembership: DataProductMembershipGet,
    NotificationTypes.DataProductDatasetAssociation: DataProductDatasetAssociation,
    NotificationTypes.DataOutputDatasetAssociation: DataOutputDatasetAssociation,
}

NotificationConfiguration = Annotated[
    Notifications,
    Field(discriminator="configuration_type"),
]
