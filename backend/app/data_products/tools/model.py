import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM


class ToolEnvironmentOverride(Base, BaseORM):
    __tablename__ = "tool_environment_overrides"

    tool_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True
    )
    environment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("environments.id", ondelete="CASCADE"), primary_key=True
    )
    values: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)


class Tool(Base, BaseORM):
    __tablename__ = "tools"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    data_product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_products.id", ondelete="CASCADE"), nullable=False
    )
    platform_key: Mapped[str] = mapped_column(String, nullable=False)
    tool_type: Mapped[str] = mapped_column(String, nullable=False)
    base_values: Mapped[dict[str, str]] = mapped_column(JSONB, nullable=False)

    overrides: Mapped[list[ToolEnvironmentOverride]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )


def ensure_tool_exists(
    tool_id: uuid.UUID, db: Session, data_product_id: Optional[uuid.UUID] = None
) -> Tool:
    tool: Tool = ensure_exists(tool_id, db, Tool)
    if data_product_id is not None and tool.data_product_id != data_product_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Required item {tool_id} does not exist",
        )
    return tool
