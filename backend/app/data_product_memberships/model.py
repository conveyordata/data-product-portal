import uuid

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.data_product_memberships.enums import DataProductUserRole
from app.database.database import Base
from app.role_assignments.enums import DecisionStatus
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

    # Foreign keys
    data_product_id: Mapped[UUID] = mapped_column(ForeignKey("data_products.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    denied_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    __table_args__ = (
        UniqueConstraint("data_product_id", "user_id", name="unique_data_product_user"),
    )
