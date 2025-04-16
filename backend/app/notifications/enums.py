from enum import Enum


class NotificationTypes(str, Enum):
    DataProductDatasetNotification = "DataProductDatasetNotification"
    DataOutputDatasetNotification = "DataOutputDatasetNotification"
    DataProductMembershipNotification = "DataProductMembershipNotification"


class NotificationOrigins(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    DENIED = "denied"
