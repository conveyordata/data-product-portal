import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, Column, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.database.database import Base, ensure_exists
from app.database.deprecated_models.data_product_membership import DataProductMembership
from app.datasets.model import datasets_owner_table
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_outputs_datasets.model import DataOutputDatasetAssociation
    from app.data_products_datasets.model import DataProductDatasetAssociation
    from app.datasets.model import Dataset


class User(Base, BaseORM):
    __tablename__ = "users"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    external_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_admin = Column(Boolean, server_default="false", nullable=False)

    # Relationships - Data Products
    data_product_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.user_id",
        back_populates="user",
        lazy="raise",
        passive_deletes=True,
        cascade="none",
    )
    approved_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.approved_by_id",
        back_populates="approved_by",
        lazy="raise",
        passive_deletes=True,
        cascade="none",
    )
    denied_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.denied_by_id",
        back_populates="denied_by",
        lazy="raise",
        passive_deletes=True,
        cascade="none",
    )
    requested_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.requested_by_id",
        back_populates="requested_by",
        lazy="raise",
        passive_deletes=True,
        cascade="none",
    )

    # Relationships - Datasets
    owned_datasets: Mapped[list["Dataset"]] = relationship(
        secondary=datasets_owner_table,
        back_populates="owners",
        # Deliberately lazy:
        #  - Used in limited cases, only on a single user
        #  - Complicates get_authenticated_user
        lazy="select",
    )
    requested_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        foreign_keys="DataProductDatasetAssociation.requested_by_id",
        back_populates="requested_by",
        lazy="raise",
    )
    denied_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        foreign_keys="DataProductDatasetAssociation.denied_by_id",
        back_populates="denied_by",
        lazy="raise",
    )
    approved_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        foreign_keys="DataProductDatasetAssociation.approved_by_id",
        back_populates="approved_by",
        lazy="raise",
    )

    # Relationships - Data outputs
    requested_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        foreign_keys="DataOutputDatasetAssociation.requested_by_id",
        back_populates="requested_by",
        lazy="raise",
    )
    denied_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        foreign_keys="DataOutputDatasetAssociation.denied_by_id",
        back_populates="denied_by",
        lazy="raise",
    )
    approved_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        foreign_keys="DataOutputDatasetAssociation.approved_by_id",
        back_populates="approved_by",
        lazy="raise",
    )

    data_product_role_assignments: Mapped[list["DataProductRoleAssignment"]] = (
        relationship(
            "DataProductRoleAssignment",
            foreign_keys="DataProductRoleAssignment.user_id",
            back_populates="user",
        )
    )


def ensure_user_exists(user_id: UUID, db: Session) -> User:
    return ensure_exists(user_id, db, User)
