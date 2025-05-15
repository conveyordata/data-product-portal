from itertools import chain

from sqlalchemy.orm import Session

from app.data_outputs_datasets.service import DataOutputDatasetService
from app.data_products_datasets.service import DataProductDatasetService
from app.pending_actions.schema import PendingAction
from app.role_assignments.data_product.service import RoleAssignmentService
from app.users.schema import User


class PendingActionsService:

    def get_user_pending_actions(
        self, db: Session, authenticated_user: User
    ) -> list[PendingAction]:
        data_product_dataset_actions = (
            DataProductDatasetService().get_user_pending_actions(db, authenticated_user)
        )
        data_output_dataset_actions = (
            DataOutputDatasetService().get_user_pending_actions(db, authenticated_user)
        )
        data_product_membership_role_actions = RoleAssignmentService(
            db=db, user=authenticated_user
        ).get_user_pending_data_product_assignments(authenticated_user)

        return sorted(
            chain(
                data_product_dataset_actions,
                data_output_dataset_actions,
                data_product_membership_role_actions,
            ),
            key=lambda action: (action.requested_on is None, action.requested_on),
        )
