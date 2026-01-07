from enum import Enum
from warnings import deprecated


@deprecated("Use PendingActionTypes instead")
class PendingActionTypesOld(str, Enum):
    DataProductDataset = "DataProductDataset"
    DataOutputDataset = "DataOutputDataset"
    DataProductRoleAssignment = "DataProductRoleAssignment"


class PendingActionTypes(str, Enum):
    DataProductOutputPort = "DataProductOutputPort"
    TechnicalAssetOutputPort = "TechnicalAssetOutputPort"
    DataProductRoleAssignment = "DataProductRoleAssignment"
