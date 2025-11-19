from typing import Final, Sequence
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.users.model import User as UserModel
from app.users.model import ensure_user_exists
from app.users.schema_request import CanBecomeAdminUpdate, UserCreate
from app.users.schema_response import UsersGet

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
        # for user in users:
        #     print(user)
        #     if (user.global_role):
        #         print(user.first_name, user.last_name)
        #         print(user.global_role.role.name)
        return users

    def remove_user(self, id: UUID) -> None:
        user = ensure_user_exists(id, self.db)
        user.data_products = []
        user.owned_datasets = []
        self.db.delete(user)
        self.db.commit()

    def create_user(self, user: UserCreate) -> dict[str, UUID]:
        user = UserModel(**user.parse_pydantic_schema())
        self.db.add(user)
        self.db.commit()
        return {"id": user.id}

    def mark_tour_as_seen(self, user_id: UUID) -> None:
        user = ensure_user_exists(user_id, self.db)
        user.has_seen_tour = True
        self.db.commit()

    def can_become_admin(self, request: CanBecomeAdminUpdate) -> None:
        # TODO ensure at least 1 admin has this privilege
        if not request.can_become_admin:
            if (
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
