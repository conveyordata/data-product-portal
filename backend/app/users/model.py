import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, Column, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_product_memberships.model import DataProductMembership
from app.data_products.model import DataProduct
from app.database.database import Base, ensure_exists
from app.datasets.model import datasets_owner_table
from app.shared.model import BaseORM
from app.users.schema import User as UserSchema

if TYPE_CHECKING:
    from app.data_outputs_datasets.model import DataOutputDatasetAssociation
    from app.data_products_datasets.model import DataProductDatasetAssociation
    from app.datasets.model import Dataset
    from app.notifications.model import Notification


def ensure_user_exists(user_id: UUID, db: Session) -> UserSchema:
    return ensure_exists(user_id, db, User)


class User(Base, BaseORM):
    __tablename__ = "users"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    external_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    is_admin = Column(Boolean, server_default="false", nullable=False)

    data_product_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.user_id",
        back_populates="user",
    )
    approved_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.approved_by_id",
        back_populates="approved_by",
    )
    denied_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.denied_by_id",
        back_populates="denied_by",
    )
    requested_memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        foreign_keys="DataProductMembership.requested_by_id",
        back_populates="requested_by",
    )
    data_products: Mapped[list["DataProduct"]] = association_proxy(
        "data_product_memberships", "data_product"
    )
    owned_datasets: Mapped[list["Dataset"]] = relationship(
        secondary=datasets_owner_table, back_populates="owners"
    )
    requested_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        foreign_keys="DataProductDatasetAssociation.requested_by_id",
        back_populates="requested_by",
    )
    denied_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        foreign_keys="DataProductDatasetAssociation.denied_by_id",
        back_populates="denied_by",
    )
    approved_datasets: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        foreign_keys="DataProductDatasetAssociation.approved_by_id",
        back_populates="approved_by",
    )
    requested_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        foreign_keys="DataOutputDatasetAssociation.requested_by_id",
        back_populates="requested_by",
    )
    denied_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        foreign_keys="DataOutputDatasetAssociation.denied_by_id",
        back_populates="denied_by",
    )
    approved_dataoutputs: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        foreign_keys="DataOutputDatasetAssociation.approved_by_id",
        back_populates="approved_by",
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="user"
    )
