import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String, func, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, column_property, mapped_column, relationship

from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_types.model import DataProductType
from app.configuration.domains.model import Domain
from app.configuration.tags.model import Tag, tag_data_product_table
from app.data_products.output_ports.model import (
    DataProductDatasetAssociation,
)
from app.data_products.status import DataProductStatus
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.configuration.data_product_lifecycles.model import DataProductLifecycle
    from app.configuration.data_product_settings.model import DataProductSettingValue
    from app.data_products.output_ports.model import (
        Dataset,
    )


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
    usage = Column(String, nullable=True)

    # Foreign keys
    type_id: Mapped[UUID] = mapped_column(ForeignKey("data_product_types.id"))
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )
    domain_id: Mapped[UUID] = Column(ForeignKey("domains.id"))

    # Relationships
    type: Mapped[DataProductType] = relationship(
        back_populates="data_products", lazy="joined"
    )
    lifecycle: Mapped["DataProductLifecycle"] = relationship(
        back_populates="data_products", lazy="joined"
    )
    domain: Mapped[Domain] = relationship(back_populates="data_products", lazy="joined")
    assignments: Mapped[list["DataProductRoleAssignment"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductRoleAssignment.decision, DataProductRoleAssignment.requested_on",
        lazy="raise",
    )
    dataset_links: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductDatasetAssociation.status.desc()",
        lazy="raise",
    )
    datasets: Mapped[list["Dataset"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_data_product_table, back_populates="data_products", lazy="raise"
    )
    data_product_settings: Mapped[list["DataProductSettingValue"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.data_product_id",
        lazy="raise",
    )
    data_outputs: Mapped[list["TechnicalAsset"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="raise",
    )

    user_count = column_property(
        select(func.count(DataProductRoleAssignment.id))
        .where(DataProductRoleAssignment.data_product_id == id)
        .where(DataProductRoleAssignment.decision == DecisionStatus.APPROVED)
        .correlate_except(DataProductRoleAssignment)
        .scalar_subquery()
    )

    dataset_count = column_property(
        select(func.count(DataProductDatasetAssociation.id))
        .where(DataProductDatasetAssociation.data_product_id == id)
        .where(DataProductDatasetAssociation.status == DecisionStatus.APPROVED)
        .correlate_except(DataProductDatasetAssociation)
        .scalar_subquery()
    )

    data_outputs_count = column_property(
        select(func.count(TechnicalAsset.id))
        .where(TechnicalAsset.owner_id == id)
        .correlate_except(TechnicalAsset)
        .scalar_subquery()
    )


def ensure_data_product_exists(
    data_product_id: UUID, db: Session, **kwargs
) -> DataProduct:
    return ensure_exists(data_product_id, db, DataProduct, **kwargs)
