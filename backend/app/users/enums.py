from enum import Enum


class RequestTypes(str, Enum):
    InputPort = "InputPort"
    TechnicalAssetOutputPort = "TechnicalAssetOutputPort"
    DataProductRoleAssignment = "DataProductRoleAssignment"
