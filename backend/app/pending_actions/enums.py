from enum import Enum


class PendingActionTypesOld(str, Enum):
    DataProductDataset = "DataProductDataset"
    DataOutputDataset = "DataOutputDataset"
    DataProductRoleAssignment = "DataProductRoleAssignment"


class PendingActionTypes(str, Enum):
    DataProductOutputPort = "DataProductOutputPort"
    TechnicalAssetOutputPort = "TechnicalAssetOutputPort"
    DataProductRoleAssignment = "DataProductRoleAssignment"
