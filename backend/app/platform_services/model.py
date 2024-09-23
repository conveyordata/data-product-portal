import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.platforms.model import Platform


class PlatformService(Base, BaseORM):
    __tablename__ = "platform_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))

    platform: Mapped["Platform"] = relationship(backref="services")
