from enum import Enum


class PendingActionTypes(str, Enum):
    DataProductDatasetAction = "DataProductDatasetAction"
    DataOutputDatasetAction = "DataOutputDatasetAction"
    DataProductMembershipAction = "DataProductMembershipAction"
