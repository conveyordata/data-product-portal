import uuid
from typing import TYPE_CHECKING, Sequence, Any

from sqlalchemy import UUID, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.database import ensure_exists
from app.events.model import Event
from app.identities.model import Identity
from app.identities.type import IdentityType

if TYPE_CHECKING:
    from app.authorization.role_assignments.output_port.model import (
        DatasetRoleAssignment,
    )
    from app.data_products.output_port_technical_assets_link.model import (
        TechnicalAssetOutputPortAssociation,
    )
    from app.data_products.output_ports.model import (
        OutputPort,
    )
    from app.explorations.model import Exploration
    from app.users.notifications.model import Notification


class User(Identity):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("identities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    events: Mapped[list[Event]] = relationship(
        "Event", back_populates="actor", foreign_keys="Event.actor_id", lazy="raise"
    )

    has_seen_tour = Column(Boolean, default=False, nullable=False)
    can_become_admin = Column(Boolean, default=False, nullable=False)
    admin_expiry = Column(DateTime(timezone=False), nullable=True)

    notifications: Mapped[list["Notification"]] = relationship(
        back_populates="user",
        foreign_keys="Notification.user_id",
        lazy="raise",
    )

    explorations: Mapped[list["Exploration"]] = relationship(
        foreign_keys="Exploration.owner_id", back_populates="owner", lazy="raise"
    )

    # Relationships - Datasets
    dataset_roles: Mapped[list["DatasetRoleAssignment"]] = relationship(
        foreign_keys="DatasetRoleAssignment.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
        # Deliberately lazy:
        #  - Used in limited cases, only on a single user
        #  - Complicates get_authenticated_user
        lazy="select",
    )
    datasets: AssociationProxy[list["OutputPort"]] = association_proxy(
        "dataset_roles", "dataset"
    )

    # Relationships - Data outputs
    requested_dataoutputs: Mapped[list["TechnicalAssetOutputPortAssociation"]] = (
        relationship(
            foreign_keys="TechnicalAssetOutputPortAssociation.requested_by_id",
            back_populates="requested_by",
            lazy="raise",
        )
    )
    denied_dataoutputs: Mapped[list["TechnicalAssetOutputPortAssociation"]] = (
        relationship(
            foreign_keys="TechnicalAssetOutputPortAssociation.denied_by_id",
            back_populates="denied_by",
            lazy="raise",
        )
    )
    approved_dataoutputs: Mapped[list["TechnicalAssetOutputPortAssociation"]] = (
        relationship(
            foreign_keys="TechnicalAssetOutputPortAssociation.approved_by_id",
            back_populates="approved_by",
            lazy="raise",
        )
    )

    __mapper_args__ = {
        "polymorphic_identity": IdentityType.USER.value,
    }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        if self.id is None or other.id is None:
            return self is other
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id) if self.id is not None else id(self)


def ensure_user_exists(user_id: UUID, db: Session, options: Sequence[Any] = ()) -> User:
    return ensure_exists(user_id, db, User, options=options)
