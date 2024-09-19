import uuid

from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.platforms.models import Platform, PlatformService
from app.shared.model import BaseORM


class Environment(Base, BaseORM):
    __tablename__ = "environments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, primary_key=True)
    context = Column(String)
    is_default = Column(Boolean, default=False)


class EnvPlatformServiceConfig(Base, BaseORM):
    __tablename__ = "env_platform_service_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id"))
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))
    service_id: Mapped[UUID] = mapped_column(ForeignKey("platform_services.id"))
    config = Column(String)

    platform: Mapped[Platform] = relationship()
    service: Mapped[PlatformService] = relationship()
    environment: Mapped[Environment] = relationship()


class EnvPlatformConfig(Base, BaseORM):
    __tablename__ = "env_platform_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id"))
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))
    config = Column(String)

    platform: Mapped[Platform] = relationship()
    environment: Mapped[Environment] = relationship()
