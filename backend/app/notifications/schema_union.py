from typing import Union

from app.data_outputs_datasets.model import (
    DataOutputDatasetAssociation as DataOutputDatasetAssociationModel,
)
from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_memberships.model import (
    DataProductMembership as DataProductMembershipModel,
)
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_products_datasets.model import (
    DataProductDatasetAssociation as DataProductDatasetAssociationModel,
)
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.notifications.notification_types import NotificationTypes

NotificationMap = {
    NotificationTypes.DataProductDatasetNotification: (
        DataProductDatasetAssociationModel
    ),
    NotificationTypes.DataOutputDatasetNotification: (
        DataOutputDatasetAssociationModel
    ),
    NotificationTypes.DataProductMembershipNotification: (DataProductMembershipModel),
}

NotificationReferenceUnion = Union[
    DataProductMembershipGet,
    DataProductDatasetAssociation,
    DataOutputDatasetAssociation,
]
