from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from starlette import status

from app.abstract_data_product.model import AbstractDataProduct, AbstractDataProductType
from app.database.database import ensure_exists

if TYPE_CHECKING:
    from app.users.model import User


class Exploration(AbstractDataProduct):
    __tablename__ = "explorations"

    id: Mapped[UUID] = mapped_column(
        "id", ForeignKey("abstract_data_products.id"), primary_key=True
    )
    __mapper_args__ = {
        "polymorphic_identity": AbstractDataProductType.EXPLORATION,
    }
    owner_id: Mapped[UUID] = mapped_column("owner_id", ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], lazy="raise")


def ensure_exploration_exists(
    id: UUID, db: Session, authenticated_user: "User", **kwargs
) -> Exploration:
    exp: Exploration = ensure_exists(id, db, Exploration, **kwargs)
    if exp.owner_id != authenticated_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Exploration access denied: you are not the owner",
        )
    return exp
