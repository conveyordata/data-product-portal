from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import UUID, Column, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.authorization.role_assignments.enums import DecisionStatus
from app.database.database import Base
from app.shared.model import BaseORM, UTCDateTime, utcnow

if TYPE_CHECKING:
    from app.authorization.roles.model import Role
    from app.identities.model import Identity
    from app.users.model import User


class GlobalRoleAssignment(Base, BaseORM):
    __tablename__ = "role_assignments_global"
    __table_args__ = (UniqueConstraint("identity_id", name="unique_global_assignment"),)

    id = Column(UUID, primary_key=True, default=uuid4)
    identity_id: Mapped[UUID] = mapped_column(
        "identity_id", ForeignKey("identities.id")
    )
    identity: Mapped["Identity"] = relationship(
        back_populates="global_role", foreign_keys=[identity_id]
    )
    role_id: Mapped[UUID] = mapped_column("role_id", ForeignKey("roles.id"))
    role: Mapped["Role"] = relationship(foreign_keys=[role_id])
    decision: Mapped[DecisionStatus] = mapped_column(
        Enum(DecisionStatus), default=DecisionStatus.PENDING
    )

    requested_on = Column(UTCDateTime(), server_default=utcnow())
    requested_by_id: Mapped[UUID] = mapped_column(UUID)
    requested_by: Mapped["User | None"] = relationship(
        primaryjoin="foreign(GlobalRoleAssignment.requested_by_id) == User.id"
    )
    deleted_requested_by_identifier: Mapped[str | None] = mapped_column()
    decided_on = Column(UTCDateTime())
    decided_by_id: Mapped[UUID] = mapped_column(UUID)
    decided_by: Mapped["User | None"] = relationship(
        primaryjoin="foreign(GlobalRoleAssignment.decided_by_id) == User.id"
    )
    deleted_decided_by_identifier: Mapped[str | None] = mapped_column()
