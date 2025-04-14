from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.users.model import User
    from app.notifications.model import Notification


import uuid

from app.shared.model import BaseORM


class NotificationInteraction(Base, BaseORM):
    __tablename__ = "notification_interactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id: Mapped[uuid.UUID] = mapped_column(
        "notification_id", ForeignKey("notifications.id", ondelete="CASCADE")
    )
    notification: Mapped["Notification"] = relationship(
        "Notification", back_populates="notification_interactions"
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="notification_interactions",
        order_by="User.last_name, User.first_name",
    )
