from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_product_memberships.enums import (
    DataProductMembershipStatus,
    DataProductUserRole,
)
from app.database.database import Base

if TYPE_CHECKING:
    from app.users.model import User
    from app.data_products.model import DataProduct

import uuid

from app.shared.model import BaseORM, utcnow


class DataProductMembership(Base, BaseORM):
    __tablename__ = "data_product_memberships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_product_id: Mapped[uuid.UUID] = mapped_column(
        "data_product_id", ForeignKey("data_products.id")
    )
    user_id: Mapped[uuid.UUID] = mapped_column("user_id", ForeignKey("users.id"))
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="data_product_memberships",
        order_by="User.last_name, User.first_name",
    )
    role: Mapped[DataProductUserRole] = mapped_column(
        Enum(DataProductUserRole), default=DataProductUserRole.MEMBER
    )
    status: Mapped[DataProductMembershipStatus] = mapped_column(
        Enum(DataProductMembershipStatus),
        default=DataProductMembershipStatus.PENDING_APPROVAL,
    )
    data_product: Mapped["DataProduct"] = relationship(
        "DataProduct", back_populates="memberships", order_by="DataProduct.name"
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id], back_populates="requested_memberships"
    )
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped["User"] = relationship(
        foreign_keys=[approved_by_id], back_populates="approved_memberships"
    )
    approved_on = Column(DateTime(timezone=False))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by: Mapped["User"] = relationship(
        foreign_keys=[denied_by_id], back_populates="denied_memberships"
    )
    notifications = relationship(
        "DataProductMembershipNotification",
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="data_product_membership",
    )
    denied_on = Column(DateTime(timezone=False))
    __table_args__ = (
        UniqueConstraint("data_product_id", "user_id", name="unique_data_product_user"),
    )

    def remove_notifications(self, db: Session):
        for notification in self.notifications:
            db.delete(notification)
        self.notifications.clear()
