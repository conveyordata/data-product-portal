import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.platforms.models import Platform
    from app.environments.model import Environment

from app.shared.model import BaseORM


class EnvironmentPlatformConfiguration(Base, BaseORM):
    __tablename__ = "env_platform_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environment_id: Mapped[UUID] = mapped_column(ForeignKey("environments.id"))
    platform_id: Mapped[UUID] = mapped_column(ForeignKey("platforms.id"))
    config = Column(String)

    platform: Mapped["Platform"] = relationship()
    environment: Mapped["Environment"] = relationship()
