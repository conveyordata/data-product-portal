from itertools import chain

from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService,
)
from app.data_products.output_port_technical_assets_link.service import (
    DataOutputDatasetService,
)
from app.data_products.output_ports.input_ports.service import InputPortService
from app.pending_actions.schema import (
    DataProductRoleAssignmentPendingAction,
)
from app.pending_actions.schema_response import PendingActionResponse
from app.users.schema import User


class PendingActionsService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_pending_actions(self, user: User) -> PendingActionResponse:
        input_port_actions = InputPortService(self.db).get_user_pending_actions(user)

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
                    input_port_actions,
                    data_output_dataset_actions,
                    data_product_role_assignment_actions,
                ),
                key=lambda action: (action.requested_on is None, action.requested_on),
            )
        )
