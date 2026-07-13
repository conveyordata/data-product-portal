from itertools import chain
from typing import Final, Sequence
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService,
)
from app.data_products.output_port_technical_assets_link.service import (
    DataOutputDatasetService,
)
from app.data_products.output_ports.input_ports.service import InputPortService
from app.users.model import User, ensure_user_exists
from app.users.model import User as UserModel
from app.users.schema_request import CanBecomeAdminUpdate, UserCreate
from app.users.schema_response import (
    MyRequestsResponse,
    PendingActionResponse,
    Request,
    UserCreateResponse,
    UsersGet,
)

SYSTEM_ACCOUNT: Final[str] = "systemaccount@noreply.com"


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self) -> Sequence[UsersGet]:
        users = self.db.scalars(
            select(UserModel)
            .outerjoin(UserModel.global_role)
            .where(UserModel.email != SYSTEM_ACCOUNT)
            .order_by(asc(UserModel.last_name), asc(UserModel.first_name))
        ).all()
        return users

    def remove_user(self, id: UUID) -> None:
        user = ensure_user_exists(id, self.db)
        user.data_products = []
        user.owned_datasets = []
        self.db.delete(user)
        self.db.commit()

    def create_user(self, user: UserCreate) -> UserCreateResponse:
        user = UserModel(**user.parse_pydantic_schema())
        self.db.add(user)
        self.db.commit()
        return UserCreateResponse(id=user.id)

    def mark_tour_as_seen(self, user_id: UUID) -> None:
        user = ensure_user_exists(user_id, self.db)
        user.has_seen_tour = True
        self.db.commit()

    def set_can_become_admin(self, request: CanBecomeAdminUpdate) -> None:
        if not request.can_become_admin and (
            len(
                self.db.scalars(
                    select(UserModel).where(UserModel.can_become_admin)
                ).all()
            )
            <= 1
        ):
            raise ValueError("At least one user must be able to become admin.")
        user = ensure_user_exists(request.user_id, self.db)
        user.can_become_admin = request.can_become_admin
        self.db.commit()

    def get_user_pending_actions(self, user: User) -> PendingActionResponse:
        input_port_actions = InputPortService(self.db).get_user_pending_actions(user)

        data_output_dataset_actions = DataOutputDatasetService(
            self.db
        ).get_user_pending_actions(user)
        data_product_role_assignment_actions = RoleAssignmentService(
            self.db
        ).get_pending_data_product_role_assignments(user)
        return PendingActionResponse(
            pending_actions=sorted(
                chain[Request](
                    input_port_actions,
                    data_output_dataset_actions,
                    data_product_role_assignment_actions,
                ),
                key=lambda action: (action.requested_on is None, action.requested_on),
            )
        )

    def get_user_requests(self, user: User) -> MyRequestsResponse:
        input_port_requests = InputPortService(self.db).get_user_requests(user)
        technical_asset_output_port_requests = DataOutputDatasetService(
            self.db
        ).get_user_requests(user)
        data_product_role_requests = RoleAssignmentService(self.db).get_user_requests(
            user
        )
        return MyRequestsResponse(
            my_requests=sorted(
                chain[Request](
                    input_port_requests,
                    technical_asset_output_port_requests,
                    data_product_role_requests,
                ),
                key=lambda action: (action.requested_on is None, action.requested_on),
            )
        )
