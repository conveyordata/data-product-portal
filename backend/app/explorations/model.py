from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.type import AbstractDataProductType
from app.core.webhooks.events import (
    ExplorationCreatedEvent,
    ExplorationDeletedEvent,
    ExplorationPayload,
    ExplorationUpdatedEvent,
)
from app.database.database import ensure_exists
from app.database.event_mixin import EventTrackedMixin

if TYPE_CHECKING:
    from app.users.model import User


class Exploration(
    AbstractDataProduct,
    EventTrackedMixin,
    create_event=ExplorationCreatedEvent,
    update_event=ExplorationUpdatedEvent,
    delete_event=ExplorationDeletedEvent,
):
    __tablename__ = "explorations"

    id: Mapped[UUID] = mapped_column(
        "id", ForeignKey("abstract_data_products.id"), primary_key=True
    )
    __mapper_args__ = {
        "polymorphic_identity": AbstractDataProductType.EXPLORATION,
    }
    owner_id: Mapped[UUID] = mapped_column("owner_id", ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], lazy="raise")

    def to_event(self) -> ExplorationPayload:
        return ExplorationPayload(
            id=self.id,
        )


def ensure_exploration_exists(
    id: UUID, db: Session, authenticated_user: "User", **kwargs
) -> Exploration:
    return ensure_exists(id, db, Exploration, **kwargs)
