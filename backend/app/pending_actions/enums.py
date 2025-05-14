from enum import Enum


class PendingActionTypes(str, Enum):
    DataProductDataset = "DataProductDataset"
    DataOutputDataset = "DataOutputDataset"
    DataProductMembership = "DataProductMembership"
    DataProductRoleAssignment = "DataProductRoleAssignment"
