from itertools import chain
from typing import Sequence

from sqlalchemy.orm import Session

from app.data_outputs_datasets.service import DataOutputDatasetService
from app.data_products_datasets.service import DataProductDatasetService
from app.pending_actions.schema import PendingAction
from app.role_assignments.data_product.service import RoleAssignmentService
from app.users.schema import User


class PendingActionsService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_pending_actions(self, user: User) -> Sequence[PendingAction]:
        data_product_dataset_actions = DataProductDatasetService(
            self.db
        ).get_user_pending_actions(user)
        data_output_dataset_actions = DataOutputDatasetService(
            self.db
        ).get_user_pending_actions(user)
        data_product_role_assignment_actions = RoleAssignmentService(
            self.db
        ).get_pending_data_product_role_assignments(user)

        return sorted(
            chain(
                data_product_dataset_actions,
                data_output_dataset_actions,
                data_product_role_assignment_actions,
            ),
            key=lambda action: (action.requested_on is None, action.requested_on),
        )
