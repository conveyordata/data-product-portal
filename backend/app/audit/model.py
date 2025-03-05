import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.users.model import User


class AuditLog(Base, BaseORM):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action = Column(String)
    subject_id = Column(UUID(as_uuid=True))
    target_id = Column(UUID(as_uuid=True))
    user_id: Mapped[uuid.UUID] = mapped_column("user_id", ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="audit_logs",
        order_by="User.last_name, User.first_name",
    )
