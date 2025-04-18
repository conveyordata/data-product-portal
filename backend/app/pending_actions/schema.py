from typing import Literal, Union

from app.data_outputs_datasets.schema import DataOutputDatasetAssociation
from app.data_product_memberships.schema_get import DataProductMembershipGet
from app.data_products_datasets.schema import DataProductDatasetAssociation
from app.pending_actions.enums import PendingActionTypes


class DataProductDatasetAction(DataProductDatasetAssociation):
    pending_action_type: Literal[PendingActionTypes.DataProductDatasetAction]


class DataOutputDatasetAction(DataOutputDatasetAssociation):
    pending_action_type: Literal[PendingActionTypes.DataOutputDatasetAction]


class DataProductMembershipAction(DataProductMembershipGet):
    pending_action_type: Literal[PendingActionTypes.DataProductMembershipAction]

PendingAction = Union[
    DataProductDatasetAction,
    DataOutputDatasetAction,
    DataProductMembershipAction,
]