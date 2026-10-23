from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.configuration.environments.model import Environment


class PlatformEnvironmentSettings(Base, BaseORM):
    __tablename__ = "platform_environment_settings"

    platform_key: Mapped[str] = mapped_column(String, primary_key=True)
    environment_id: Mapped[UUID] = mapped_column(
        ForeignKey("environments.id", ondelete="CASCADE"), primary_key=True
    )
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False)

    environment: Mapped["Environment"] = relationship(lazy="joined")
