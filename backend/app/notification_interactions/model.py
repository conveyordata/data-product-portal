from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.notifications.model import Notification

if TYPE_CHECKING:
    from app.users.model import User

import uuid

from app.shared.model import BaseORM


class NotificationInteraction(Base, BaseORM):
    __tablename__ = "notification_interactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id: Mapped[uuid.UUID] = mapped_column(
        "notification_id", ForeignKey("notifications.id")
    )
    notification: Mapped["Notification"] = relationship(
        "Notification", back_populates="notification_interactions"
    )
    user_id: Mapped[uuid.UUID] = mapped_column("user_id", ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="notification_interactions",  # deze lijn nachecken
        order_by="User.last_name, User.first_name",
    )
    last_seen = Column(DateTime(timezone=False))
    last_interaction = Column(DateTime(timezone=False))
    # __table_args__ = (
    # UniqueConstraint("data_product_id", "user_id", name="unique_data_product_user"),
    # ) deze lijn nachecken
