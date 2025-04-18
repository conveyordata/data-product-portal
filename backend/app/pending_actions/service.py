

from sqlalchemy.orm import Session


from app.data_outputs_datasets.service import DataOutputDatasetService
from app.data_product_memberships.service import DataProductMembershipService
from app.data_products_datasets.service import DataProductDatasetService
from app.pending_actions.enums import PendingActionTypes
from app.pending_actions.schema import DataOutputDatasetAction, DataProductDatasetAction, DataProductMembershipAction, PendingAction
from app.users.schema import User


class PendingActionService:

    def get_user_pending_actions(
        self, db: Session, authenticated_user: User
    ) -> list[PendingAction]:
        return
