from itertools import chain
from typing import Sequence

from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService,
)
from app.data_products.output_port_technical_assets_link.service import (
    DataOutputDatasetService,
)
from app.data_products.output_ports.input_ports.service import DataProductDatasetService
from app.pending_actions.schema import (
    DataProductRoleAssignmentPendingAction,
    PendingActionOld,
)
from app.pending_actions.schema_response import PendingActionResponse
from app.users.schema import User


class PendingActionsService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_pending_actions_old(self, user: User) -> Sequence[PendingActionOld]:
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

    def get_user_pending_actions(self, user: User) -> PendingActionResponse:
        data_product_dataset_actions = [
            action.convert()
            for action in DataProductDatasetService(self.db).get_user_pending_actions(
                user
            )
        ]

        data_output_dataset_actions = [
            action.convert()
            for action in DataOutputDatasetService(self.db).get_user_pending_actions(
                user
            )
        ]
        data_product_role_assignment_actions = [
            DataProductRoleAssignmentPendingAction.model_validate(action)
            for action in RoleAssignmentService(
                self.db
            ).get_pending_data_product_role_assignments(user)
        ]
        return PendingActionResponse(
            pending_actions=sorted(
                chain(
                    data_product_dataset_actions,
                    data_output_dataset_actions,
                    data_product_role_assignment_actions,
                ),
                key=lambda action: (action.requested_on is None, action.requested_on),
            )
        )
