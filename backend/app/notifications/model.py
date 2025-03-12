import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from app.notification_interactions.model import NotificationInteraction

from app.database.database import Base
from app.notifications.notification_types import NotificationTypes
from app.shared.model import BaseORM


class Notification(Base, BaseORM):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_type: Mapped[NotificationTypes] = Column(Enum(NotificationTypes))
    notification_interactions: Mapped[list["NotificationInteraction"]] = relationship(
        "NotificationInteraction",
        back_populates="notification",
        cascade="all, delete-orphan",
    )
    __mapper_args__ = {
        "polymorphic_on": "configuration_type",
        "polymorphic_identity": "notification",
    }
