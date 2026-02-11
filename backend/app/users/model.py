import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, Column, DateTime, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.database import Base, ensure_exists
from app.events.model import Event
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.authorization.role_assignments.data_product.model import (
        DataProductRoleAssignment,
    )
    from app.authorization.role_assignments.global_.model import (
        GlobalRoleAssignment,
    )
    from app.authorization.role_assignments.output_port.model import (
        DatasetRoleAssignment,
    )
    from app.data_products.model import DataProduct
    from app.data_products.output_port_technical_assets_link.model import (
        DataOutputDatasetAssociation,
    )
    from app.data_products.output_ports.model import (
        DataProductDatasetAssociation,
        Dataset,
    )
    from app.users.notifications.model import Notification


class User(Base, BaseORM):
    __tablename__ = "users"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    external_id = Column(String)
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

    # Relationships - Data Products
    data_product_roles: Mapped[list["DataProductRoleAssignment"]] = relationship(
        foreign_keys="DataProductRoleAssignment.user_id",
        back_populates="user",
        # Deliberately lazy:
        #  - Used in limited cases, only on a single user
        #  - Complicates get_authenticated_user
        #  - Private dataset test cases become more complex
        #    (need to manipulate the session to avoid a user being cached with a
        #     membership field with raise load strategy)
        lazy="select",
    )
    data_products: Mapped[list["DataProduct"]] = association_proxy(
        "data_product_roles", "data_product"
    )

    global_role: Mapped["GlobalRoleAssignment"] = relationship(
        foreign_keys="GlobalRoleAssignment.user_id",
        back_populates="user",
        # Deliberately lazy:
        #  - Used in limited cases, only on a single user
        #  - Complicates get_authenticated_user
        #  - Private dataset test cases become more complex
        #    (need to manipulate the session to avoid a user being cached with a
        #     membership field with raise load strategy)
        lazy="select",
    )

    # Relationships - Datasets
    dataset_roles: Mapped[list["DatasetRoleAssignment"]] = relationship(
        foreign_keys="DatasetRoleAssignment.user_id",
        back_populates="user",
        # Deliberately lazy:
        #  - Used in limited cases, only on a single user
        #  - Complicates get_authenticated_user
        lazy="select",
    )
    datasets: Mapped[list["Dataset"]] = association_proxy("dataset_roles", "dataset")
    requested_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        foreign_keys="DataProductDatasetAssociation.requested_by_id",
        back_populates="requested_by",
        lazy="raise",
    )
    denied_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        foreign_keys="DataProductDatasetAssociation.denied_by_id",
        back_populates="denied_by",
        lazy="raise",
    )
    approved_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        foreign_keys="DataProductDatasetAssociation.approved_by_id",
        back_populates="approved_by",
        lazy="raise",
    )

    # Relationships - Data outputs
    requested_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        foreign_keys="DataOutputDatasetAssociation.requested_by_id",
        back_populates="requested_by",
        lazy="raise",
    )
    denied_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        foreign_keys="DataOutputDatasetAssociation.denied_by_id",
        back_populates="denied_by",
        lazy="raise",
    )
    approved_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        foreign_keys="DataOutputDatasetAssociation.approved_by_id",
        back_populates="approved_by",
        lazy="raise",
    )


def ensure_user_exists(user_id: UUID, db: Session) -> User:
    return ensure_exists(user_id, db, User)
