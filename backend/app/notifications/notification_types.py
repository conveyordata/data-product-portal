from enum import Enum


class NotificationTypes(str, Enum):
    DataProductDatasetAssociation = "DataProductDatasetAssociation"
    DataOutputDatasetAssociation = "DataOutputDatasetAssociation"
    DataProductMembership = "DataProductMembership"
