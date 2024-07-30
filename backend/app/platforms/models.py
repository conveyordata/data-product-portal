import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM


class Platform(Base):
    __tablename__ = "platforms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)


class PlatformService(Base):
    __tablename__ = "platform_services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))

    platform: Mapped[Platform] = relationship(backref="services")


class PlatformServiceConfig(Base, BaseORM):
    __tablename__ = "platform_service_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))
    service_id: Mapped[UUID] = mapped_column(ForeignKey("platform_services.id"))
    config = Column(String)

    platform: Mapped[Platform] = relationship()
    service: Mapped[PlatformService] = relationship()
