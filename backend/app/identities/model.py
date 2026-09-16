import uuid

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM

from typing import TYPE_CHECKING

# Added for type checking in the IDE, disabled at runtime to avoid circular dependencies
if TYPE_CHECKING:
    from app.authorization.role_assignments.data_product.model import (
        DataProductRoleAssignment,
    )
    from app.authorization.role_assignments.global_.model import (
        GlobalRoleAssignment,
    )
    from app.data_products.model import DataProduct


class Identity(Base, BaseORM):
    __tablename__ = "identities"
    __table_args__ = (
        CheckConstraint(
            "type IN ('user', 'group', 'machine_user')",
            name="ck_identities_type",
        ),
        UniqueConstraint(
            "type",
            "external_id",
            name="uq_identities_type_external_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    type: Mapped[str] = mapped_column(String, nullable=False)
    external_id: Mapped[str] = mapped_column(String, nullable=False)


    data_product_roles: Mapped[list["DataProductRoleAssignment"]] = relationship(
        foreign_keys="DataProductRoleAssignment.identity_id",
        back_populates="identity",
        cascade="all, delete-orphan", # TODO discuss this with the team
        lazy="raise",
    )
    data_products: AssociationProxy[list["DataProduct"]] = association_proxy(
        "data_product_roles",
        "data_product",
    )

    global_role: Mapped["GlobalRoleAssignment"] = relationship(
        foreign_keys="GlobalRoleAssignment.identity_id",
        back_populates="identity",
        cascade="all, delete-orphan",  # TODO discuss this with the team
        lazy="select",
    )

    __mapper_args__ = {
        "polymorphic_on": type
    }

def ensure_identity_exists(identity_id: UUID, db: Session, options: list = []) -> Identity:
    return ensure_exists(identity_id, db, Identity, options=options)