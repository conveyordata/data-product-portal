import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.database import Base, ensure_exists
from app.identities.model import Identity
from app.identities.type import IdentityType
from app.shared.model import BaseORM


class Group(Identity):
    __tablename__ = "groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    display_name: Mapped[str] = mapped_column(String, nullable=False)

    memberships: Mapped[list["GroupMembership"]] = relationship(
        back_populates="group",
        foreign_keys="GroupMembership.group_id",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    __mapper_args__ = {
        "polymorphic_identity": IdentityType.GROUP.value,
    }


class GroupMembership(Base, BaseORM):
    __tablename__ = "group_memberships"
    __table_args__ = (
        CheckConstraint(
            "group_id <> member_identity_id",
            name="ck_group_memberships_not_self",
        ),
    )

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("groups.id", ondelete="CASCADE"),
        primary_key=True,
    )
    member_identity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identities.id", ondelete="CASCADE"),
        primary_key=True,
    )

    group: Mapped[Group] = relationship(
        back_populates="memberships",
        foreign_keys=[group_id],
        lazy="raise",
    )
    member: Mapped[Identity] = relationship(
        foreign_keys=[member_identity_id],
        lazy="joined",
    )


def ensure_group_exists(group_id: UUID, db: Session, options: list = []) -> Group:
    return ensure_exists(group_id, db, Group, options=options)
