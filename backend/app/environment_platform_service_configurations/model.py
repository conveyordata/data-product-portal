import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.environments.model import Environment
    from app.platforms.models import Platform, PlatformService


class EnvironmentPlatformServiceConfiguration(Base, BaseORM):
    __tablename__ = "env_platform_service_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id"))
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))
    service_id: Mapped[UUID] = mapped_column(ForeignKey("platform_services.id"))
    config = Column(String)

    platform: Mapped["Platform"] = relationship()
    service: Mapped["PlatformService"] = relationship()
    environment: Mapped["Environment"] = relationship()
