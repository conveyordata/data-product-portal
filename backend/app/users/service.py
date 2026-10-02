from itertools import chain
from typing import Final, Sequence, Any
from uuid import UUID

from sqlalchemy import asc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.authorization.role_assignments.data_product.service import (
    RoleAssignmentService,
)
from app.data_products.output_port_technical_assets_link.service import (
    TechnicalAssetOutputPortService,
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
from app.identities.schema_response import (
    IdentityBatchCreateError,
    IdentityBatchCreateResponse,
)
from app.identities.service import validate_batch_create_items

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
        user = ensure_user_exists(
            id, self.db, options=[selectinload(User.data_product_roles)]
        )
        user.data_products = []
        user.datasets = []
        self.db.delete(user)
        self.db.flush()

    def create_user(self, user: UserCreate) -> UserCreateResponse:
        user = UserModel(**user.parse_pydantic_schema())
        self.db.add(user)
        self.db.flush()
        return UserCreateResponse(id=user.id)

    def mark_tour_as_seen(self, user_id: UUID) -> None:
        user = ensure_user_exists(user_id, self.db)
        user.has_seen_tour = True
        self.db.flush()

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
        self.db.flush()

    def get_user_pending_actions(self, user: User) -> PendingActionResponse:
        input_port_actions = InputPortService(self.db).get_user_pending_actions(user)

        technical_asset_output_port_actions = TechnicalAssetOutputPortService(
            self.db
        ).get_user_pending_actions(user)
        data_product_role_assignment_actions = RoleAssignmentService(
            self.db
        ).get_pending_data_product_role_assignments(user)
        return PendingActionResponse(
            pending_actions=sorted(
                chain[Request](
                    input_port_actions,
                    technical_asset_output_port_actions,
                    data_product_role_assignment_actions,
                ),
                key=lambda action: (action.requested_on is None, action.requested_on),
            )
        )

    def get_user_requests(
        self, user: User, hide_old_inactive: bool
    ) -> MyRequestsResponse:
        input_port_requests = InputPortService(self.db).get_user_requests(
            user, hide_old_inactive
        )
        technical_asset_output_port_requests = TechnicalAssetOutputPortService(
            self.db
        ).get_user_requests(user, hide_old_inactive)
        data_product_role_requests = RoleAssignmentService(self.db).get_user_requests(
            user, hide_old_inactive
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

    def create_users_batch(
            self,
            items: list[Any],
    ) -> IdentityBatchCreateResponse:
        validated_items, errors = validate_batch_create_items(
            items,
            UserCreate,
        )

        emails = set()
        external_ids = set()
        for user in validated_items:
            emails.add(user.email)
            external_ids.add(user.external_id)

        existing_users = self.db.execute(
            select(UserModel.email, UserModel.external_id).where(
                or_(
                    UserModel.email.in_(emails),
                    UserModel.external_id.in_(external_ids),
                )
            )
        ).all()

        unavailable_emails = set()
        unavailable_external_ids = set()
        for email, external_id in existing_users:
            unavailable_emails.add(email)
            unavailable_external_ids.add(external_id)

        users: list[UserModel] = []

        for user in validated_items:
            if user.email in unavailable_emails:
                errors.append(
                    IdentityBatchCreateError(
                        item=user,
                        errors=["A user with this email already exists."],
                    )
                )
                continue

            if user.external_id in unavailable_external_ids:
                errors.append(
                    IdentityBatchCreateError(
                        item=user,
                        errors=["A user with this external ID already exists."],
                    )
                )
                continue

            unavailable_emails.add(user.email)
            unavailable_external_ids.add(user.external_id)
            users.append(UserModel(**user.parse_pydantic_schema()))

        self.db.add_all(users)
        self.db.flush()

        return IdentityBatchCreateResponse(
            ids=[user.id for user in users],
            errors=errors,
        )

    def remove_users_batch(self, ids: list[UUID]) -> None:
        users = self.db.scalars(
            select(UserModel)
            .where(UserModel.id.in_(ids))
            .options(selectinload(UserModel.data_product_roles))
        ).all()

        for user in users:
            user.data_products = []
            user.datasets = []
            self.db.delete(user)

        self.db.flush()

