import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_product_memberships.model import DataProductMembership
from app.data_product_settings.model import DataProductSettingValue
from app.data_product_types.model import DataProductType
from app.data_products.status import DataProductStatus
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import Base, ensure_exists
from app.role_assignments.data_product.model import DataProductRoleAssignment
from app.role_assignments.enums import DecisionStatus
from app.shared.model import BaseORM
from app.tags.model import Tag, tag_data_product_table

if TYPE_CHECKING:
    from app.data_outputs.model import DataOutput
    from app.data_product_lifecycles.model import DataProductLifecycle
    from app.domains.model import Domain


class DataProduct(Base, BaseORM):
    __tablename__ = "data_products"

    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    namespace = Column(String)
    description = Column(String)
    about = Column(String)
    status: DataProductStatus = Column(
        Enum(DataProductStatus), default=DataProductStatus.ACTIVE
    )

    # Foreign keys
    type_id: Mapped[UUID] = mapped_column(ForeignKey("data_product_types.id"))
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )
    domain_id: Mapped[UUID] = Column(ForeignKey("domains.id"))

    # Relationships
    type: Mapped["DataProductType"] = relationship(
        back_populates="data_products", lazy="joined"
    )
    lifecycle: Mapped["DataProductLifecycle"] = relationship(
        back_populates="data_products", lazy="joined"
    )
    domain: Mapped["Domain"] = relationship(
        back_populates="data_products", lazy="joined"
    )
    memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductMembership.status, "
        "DataProductMembership.requested_on, "
        "DataProductMembership.role",
        lazy="joined",
    )
    assignments: Mapped[list["DataProductRoleAssignment"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductRoleAssignment.decision, "
        "DataProductRoleAssignment.requested_on",
        lazy="joined",
    )
    dataset_links: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductDatasetAssociation.status.desc()",
        lazy="raise",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_data_product_table, back_populates="data_products", lazy="joined"
    )
    data_product_settings: Mapped[list["DataProductSettingValue"]] = relationship(
        "DataProductSettingValue",
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.data_product_id",
        lazy="joined",
    )
    data_outputs: Mapped[list["DataOutput"]] = relationship(
        "DataOutput",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    @property
    def user_count(self) -> int:
        approved_assignments = [
            assignment
            for assignment in self.assignments
            if assignment.decision == DecisionStatus.APPROVED
        ]
        return len(approved_assignments)

    @property
    def dataset_count(self) -> int:
        accepted_dataset_links = [
            link
            for link in self.dataset_links
            if link.status == DecisionStatus.APPROVED
        ]
        return len(accepted_dataset_links)

    @property
    def data_outputs_count(self) -> int:
        return len(self.data_outputs)


def ensure_data_product_exists(
    data_product_id: UUID, db: Session, **kwargs
) -> DataProduct:
    return ensure_exists(data_product_id, db, DataProduct, **kwargs)
