from enum import Enum


class PendingActionTypes(str, Enum):
    DataProductDataset = "DataProductDataset"
    DataOutputDataset = "DataOutputDataset"
    DataProductRoleAssignment = "DataProductRoleAssignment"
