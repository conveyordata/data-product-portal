from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.data_product_memberships.enums import (
    DataProductUserRole,
)
from app.database.database import Base
from app.notifications.model import DataProductMembershipNotification
from app.role_assignments.enums import DecisionStatus

if TYPE_CHECKING:
    from app.users.model import User
    from app.data_products.model import DataProduct

import uuid

from app.shared.model import BaseORM, utcnow


class DataProductMembership(Base, BaseORM):
    __tablename__ = "data_product_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[DataProductUserRole] = mapped_column(
        Enum(DataProductUserRole), default=DataProductUserRole.MEMBER
    )
    status: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus),
        default=DecisionStatus.PENDING,
    )
    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    approved_on = Column(DateTime(timezone=False))
    denied_on = Column(DateTime(timezone=False))

    notifications = relationship(
        DataProductMembershipNotification,
        cascade="all, delete-orphan",
        passive_deletes=True,
        back_populates="data_product_membership",
    )

    # Foreign keys
    data_product_id: Mapped[UUID] = mapped_column(ForeignKey("data_products.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship(
        foreign_keys=[user_id],
        back_populates="data_product_memberships",
        order_by="User.last_name, User.first_name",
        lazy="joined",
    )
    data_product: Mapped["DataProduct"] = relationship(
        "DataProduct",
        back_populates="memberships",
        order_by="DataProduct.name",
        lazy="joined",
    )
    requested_by: Mapped["User"] = relationship(
        foreign_keys=[requested_by_id],
        back_populates="requested_memberships",
        lazy="joined",
    )
    approved_by: Mapped["User"] = relationship(
        foreign_keys=[approved_by_id],
        back_populates="approved_memberships",
        lazy="joined",
    )
    denied_by: Mapped["User"] = relationship(
        foreign_keys=[denied_by_id],
        back_populates="denied_memberships",
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint("data_product_id", "user_id", name="unique_data_product_user"),
    )
