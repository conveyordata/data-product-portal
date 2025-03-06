from enum import Enum


class NotificationTypes(str, Enum):
    DataProductDataset = "DataProductDataset"
    DataOutputDataset = "DataOutputDataset"
    DataProductMembership = "DataProductMembership"
