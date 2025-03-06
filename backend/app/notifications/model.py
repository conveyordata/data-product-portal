import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from app.notifications.enums import NotificationTrigger

if TYPE_CHECKING:
    from app.notification_interactions.model import NotificationInteraction
    from app.notifications.base_model import BaseNotificationConfiguration

from app.database.database import Base
from app.shared.model import BaseORM


class Notification(Base, BaseORM):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # external_id = Column(String) Eens navragen
    description = Column(
        String
    )  # ik denk best opstellen in backend idpv van in frontend?
    # kunt in frontend altijd nog custom via bijgevoegd object
    # status: DataOutputStatus = Column(Enum(DataOutputStatus)) Moet gemapped worden
    # naar andere table, per user_id bijhouden
    trigger = Column(Enum(NotificationTrigger))
    configuration: Mapped["BaseNotificationConfiguration"] = relationship()
    configuration_id: Mapped[UUID] = Column(
        ForeignKey("notification_configurations.id")
    )
    notification_interactions: Mapped[list["NotificationInteraction"]] = relationship(
        "NotificationInteraction",
        back_populates="notification",
        cascade="all, delete-orphan",
    )
    # tags: Mapped[list[Tag]] = relationship(secondary=tag_data_output_table) tags
    # gebruik nachecken
