from uuid import UUID

from sqlalchemy import asc, select
from sqlalchemy.orm import Session

from app.users.model import User as UserModel
from app.users.model import ensure_user_exists
from app.users.schema_request import UserCreate
from app.users.schema_response import UsersGet


class UserService:
    def get_users(self, db: Session) -> list[UsersGet]:
        return db.scalars(
            select(UserModel)
            .where(UserModel.email != "systemaccount@noreply.com")
            .order_by(asc(UserModel.last_name), asc(UserModel.first_name))
        ).all()

    def remove_user(self, id: UUID, db: Session) -> None:
        user = ensure_user_exists(id, db)
        user.data_products = []
        user.owned_datasets = []
        db.delete(user)
        db.commit()

    def create_user(self, user: UserCreate, db: Session) -> dict[str, UUID]:
        user = UserModel(**user.parse_pydantic_schema())
        db.add(user)
        db.commit()
        return {"id": user.id}
