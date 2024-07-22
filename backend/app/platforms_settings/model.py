import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

from .enums import Platforms


class PlatformSetting(Base, BaseORM):
    __tablename__ = "platforms_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(Enum(Platforms))
    settings = Column(String)
    environment: Mapped[String] = mapped_column(ForeignKey("environments.name"))

    # environment_rel = relationship("Environments", back_populates="settings")
