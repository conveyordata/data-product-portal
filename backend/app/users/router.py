from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db_session
from app.dependencies import only_for_admin
from app.users.schema import User
from app.users.service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
def get_users(db: Session = Depends(get_db_session)) -> list[User]:
    return UserService().get_users(db)


@router.delete(
    "/{id}",
    responses={
        404: {
            "description": "User not found",
            "content": {
                "application/json": {"example": {"detail": "User email not found"}}
            },
        }
    },
    dependencies=[Depends(only_for_admin)],
)
def remove_user(id: UUID, db: Session = Depends(get_db_session)):
    return UserService().remove_user(id, db)
