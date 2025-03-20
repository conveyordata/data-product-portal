import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM, utcnow

from ..enums import DecisionStatus

if TYPE_CHECKING:
    from app.data_products.model import DataProduct
    from app.roles.model import Role
    from app.users.model import User


class DataProductRoleAssignment(Base, BaseORM):
    __tablename__ = "role_assignments_data_product"
    __table_args__ = UniqueConstraint(
        "data_product_id", "user_id", name="unique_data_product_assignment"
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_product_id: Mapped[uuid.UUID] = mapped_column(
        "data_product_id", ForeignKey("data_products.id")
    )
    data_product: Mapped[DataProduct] = relationship(
        "DataProduct", foreign_keys=[data_product_id]
    )
    user_id: Mapped[uuid.UUID] = mapped_column("user_id", ForeignKey("users.id"))
    user: Mapped[User] = relationship("User", foreign_keys=[user_id])
    role_id: Mapped[uuid.UUID] = mapped_column("role_id", ForeignKey("roles.id"))
    role: Mapped[Role] = mapped_column("Role", foreign_keys=[role_id])
    decision: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus), default=DecisionStatus.PENDING
    )

    requested_on = Column(DateTime(timezone=False), server_default=utcnow())
    requested_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    requested_by: Mapped[User] = relationship(foreign_keys=[requested_by_id])
    decided_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    decided_by: Mapped[User] = relationship(foreign_keys=[decided_by_id])
    decided_on = Column(DateTime(timezone=False))
