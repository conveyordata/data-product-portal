from uuid import UUID

from sqlalchemy import asc
from sqlalchemy.orm import Session

from app.users.model import User as UserModel
from app.users.model import ensure_user_exists
from app.users.schema import User


class UserService:
    def get_users(self, db: Session) -> list[User]:
        return (
            db.query(UserModel)
            .order_by(asc(UserModel.last_name), asc(UserModel.first_name))
            .all()
        )

    def remove_user(self, id: UUID, db: Session):
        user = ensure_user_exists(id, db)
        user.data_products = []
        user.owned_datasets = []
        user.delete()
        db.commit()
