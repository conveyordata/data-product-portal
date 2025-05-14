from enum import Enum


class PendingActionTypes(str, Enum):
    DataProductDatasetPendingAction = "DataProductDatasetPendingAction"
    DataOutputDatasetPendingAction = "DataOutputDatasetPendingAction"
    DataProductMembershipPendingAction = "DataProductMembershipPendingAction"
    DataProductMembershipRolePendingAction = "DataProductMembershipRolePendingAction"
