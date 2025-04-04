import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, object_session, relationship

from app.notifications.schema_union import NotificationMap

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
    reference_id = Column(UUID(as_uuid=True), nullable=False)

    @property
    def reference(self):
        mapping = NotificationMap
        target_class = mapping.get(self.configuration_type)
        if not target_class:
            return None
        session = object_session(self)
        return session.get(target_class, self.reference_id)
