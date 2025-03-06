import uuid

from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.database.database import Base
from app.notifications.notification_types import NotificationTypes
from app.shared.model import BaseORM


class BaseNotificationConfiguration(Base, BaseORM):
    __tablename__ = "notification_configurations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_type: Mapped[NotificationTypes] = Column(Enum(NotificationTypes))

    __mapper_args__ = {
        "polymorphic_on": "configuration_type",
        "polymorphic_identity": "notification",
    }
