from typing import Sequence
from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.users.model import User as UserModel
from app.users.model import ensure_user_exists
from app.users.schema_request import UserCreate
from app.users.schema_response import UsersGet


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self) -> Sequence[UsersGet]:
        return self.db.scalars(
            select(UserModel)
            .outerjoin(UserModel.global_role)
            .where(UserModel.email != "systemaccount@noreply.com")
            .order_by(asc(UserModel.last_name), asc(UserModel.first_name))
        ).all()

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
