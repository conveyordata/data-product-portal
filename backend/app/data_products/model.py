from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, func, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, column_property, mapped_column, relationship

from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_types.model import DataProductType
from app.configuration.tags.model import Tag, tag_data_product_table
from app.core.webhooks.events import (
    DataProductEvent,
)
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import ensure_exists
from app.database.event_mixin import EventTrackedMixin

if TYPE_CHECKING:
    from app.configuration.data_product_lifecycles.model import DataProductLifecycle
    from app.configuration.data_product_settings.model import DataProductSettingValue
    from app.data_products.output_ports.model import (
        OutputPort,
    )


class DataProduct(
    AbstractDataProduct,
    EventTrackedMixin,
):
    __tablename__ = "data_products"

    id: Mapped[UUID] = mapped_column(
        "id", ForeignKey("abstract_data_products.id"), primary_key=True
    )
    about = Column(String)
    usage = Column(String, nullable=True)

    # Foreign keys
    type_id: Mapped[UUID] = mapped_column(ForeignKey("data_product_types.id"))
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )

    # Relationships
    type: Mapped[DataProductType] = relationship(
        back_populates="data_products", lazy="joined"
    )
    lifecycle: Mapped["DataProductLifecycle"] = relationship(
        back_populates="data_products", lazy="joined"
    )
    assignments: Mapped[list["DataProductRoleAssignment"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductRoleAssignment.decision, DataProductRoleAssignment.requested_on",
        lazy="raise",
    )
    datasets: Mapped[list["OutputPort"]] = relationship(
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

    data_outputs_count = column_property(
        select(func.count(TechnicalAsset.id))
        .where(TechnicalAsset.owner_id == id)
        .correlate_except(TechnicalAsset)
        .scalar_subquery()
    )

    __mapper_args__ = {
        "polymorphic_identity": AbstractDataProductType.DATA_PRODUCT,
    }

    def to_event(self) -> DataProductEvent:
        return DataProductEvent(
            id=self.id,
        )


def ensure_data_product_exists(
    data_product_id: UUID, db: Session, **kwargs
) -> DataProduct:
    return ensure_exists(data_product_id, db, DataProduct, **kwargs)
