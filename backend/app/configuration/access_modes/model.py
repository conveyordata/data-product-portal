import uuid

from sqlalchemy import UUID, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, relationship

from app.database.database import Base
from app.shared.model import BaseORM


class DefaultAccessMode(Base, BaseORM):
    __tablename__ = "default_access_modes"

    technical_asset_type = Column(String, primary_key=True)
    access_mode_id = Column(
        UUID(as_uuid=True),
        ForeignKey("access_modes.id", ondelete="CASCADE"),
        nullable=False,
    )


class AccessMode(Base, BaseORM):
    __tablename__ = "access_modes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    description = Column(String)
    technical_asset_types = Column(
        ARRAY(String), nullable=False, default=list, server_default="{}"
    )
    defaults: Mapped[list[DefaultAccessMode]] = relationship(
        order_by=DefaultAccessMode.technical_asset_type,
        viewonly=True,
        lazy="raise",
    )

    @property
    def default_for_technical_asset_types(self) -> list[str]:
        return [default.technical_asset_type for default in self.defaults]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AccessMode):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash((AccessMode, self.id))
