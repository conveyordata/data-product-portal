from enum import Enum


class NotificationTypes(str, Enum):
    DataProductDatasetNotification = "DataProductDatasetNotification"
    DataOutputDatasetNotification = "DataOutputDatasetNotification"
    DataProductMembershipNotification = "DataProductMembershipNotification"
