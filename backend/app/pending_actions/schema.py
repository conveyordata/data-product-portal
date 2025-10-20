from typing import Literal, Union

from app.authorization.role_assignments.data_product.schema import (
    DataProductRoleAssignmentResponse,
)
from app.data_outputs_datasets.schema_response import DataOutputDatasetAssociationsGet
from app.data_products_datasets.schema_response import DataProductDatasetAssociationsGet
from app.pending_actions.enums import PendingActionTypes


class DataProductDatasetPendingAction(DataProductDatasetAssociationsGet):
    pending_action_type: Literal[PendingActionTypes.DataProductDataset] = (
        PendingActionTypes.DataProductDataset
    )


class DataOutputDatasetPendingAction(DataOutputDatasetAssociationsGet):
    pending_action_type: Literal[PendingActionTypes.DataOutputDataset] = (
        PendingActionTypes.DataOutputDataset
    )


class DataProductRoleAssignmentPendingAction(DataProductRoleAssignmentResponse):
    pending_action_type: Literal[PendingActionTypes.DataProductRoleAssignment] = (
        PendingActionTypes.DataProductRoleAssignment
    )


PendingAction = Union[
    DataProductDatasetPendingAction,
    DataOutputDatasetPendingAction,
    DataProductRoleAssignmentPendingAction,
]
