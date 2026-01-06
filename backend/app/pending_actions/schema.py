from typing import Literal, Union

from app.authorization.role_assignments.data_product.schema import (
    DataProductRoleAssignmentResponse,
)
from app.data_products.output_port_technical_assets_link.schema_response import (
    DataOutputDatasetAssociationsGet,
    TechnicalAssetOutputPortAssociationsGet,
)
from app.data_products_datasets.schema_response import (
    DataProductDatasetAssociationsGet,
    DataProductOutputPortAssociationsGet,
)
from app.pending_actions.enums import PendingActionTypes, PendingActionTypesOld


class DataProductDatasetPendingAction(DataProductDatasetAssociationsGet):
    pending_action_type: Literal[PendingActionTypesOld.DataProductDataset] = (
        PendingActionTypesOld.DataProductDataset
    )


class DataProductOutputPortPendingAction(DataProductOutputPortAssociationsGet):
    pending_action_type: Literal[PendingActionTypes.DataProductOutputPort] = (
        PendingActionTypes.DataProductOutputPort
    )


class DataOutputDatasetPendingAction(DataOutputDatasetAssociationsGet):
    pending_action_type: Literal[PendingActionTypesOld.DataOutputDataset] = (
        PendingActionTypesOld.DataOutputDataset
    )


class TechnicalAssetOutputPortPendingAction(TechnicalAssetOutputPortAssociationsGet):
    pending_action_type: Literal[PendingActionTypes.TechnicalAssetOutputPort] = (
        PendingActionTypes.TechnicalAssetOutputPort
    )


class DataProductRoleAssignmentPendingActionOld(DataProductRoleAssignmentResponse):
    pending_action_type: Literal[PendingActionTypesOld.DataProductRoleAssignment] = (
        PendingActionTypesOld.DataProductRoleAssignment
    )


class DataProductRoleAssignmentPendingAction(DataProductRoleAssignmentResponse):
    pending_action_type: Literal[PendingActionTypes.DataProductRoleAssignment] = (
        PendingActionTypes.DataProductRoleAssignment
    )


PendingActionOld = Union[
    DataProductDatasetPendingAction,
    DataOutputDatasetPendingAction,
    DataProductRoleAssignmentPendingActionOld,
]

PendingAction = Union[
    DataProductOutputPortPendingAction,
    TechnicalAssetOutputPortPendingAction,
    DataProductRoleAssignmentPendingAction,
]
