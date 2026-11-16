import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    UUID,
    Column,
    ForeignKey,
    String,
    func,
    select,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import (
    Mapped,
    Session,
    column_property,
    mapped_column,
    relationship,
)

from app.abstract_data_product.model import AbstractDataProduct
from app.abstract_data_product.type import AbstractDataProductType
from app.authorization.role_assignments.data_product.model import (
    DataProductRoleAssignment,
)
from app.authorization.role_assignments.enums import DecisionStatus
from app.configuration.data_product_types.model import DataProductType
from app.configuration.environments.model import Environment
from app.configuration.tags.model import Tag, tag_data_product_table
from app.core.webhooks.events import (
    DataProductEvent,
)
from app.data_products.technical_assets.model import TechnicalAsset
from app.database.database import (
    Base,
    ensure_exists,
)
from app.database.event_mixin import EventTrackedMixin
from app.shared.model import UTCDateTime, utcnow

if TYPE_CHECKING:
    from app.configuration.data_product_lifecycles.model import DataProductLifecycle
    from app.configuration.data_product_settings.model import DataProductSettingValue
    from app.data_products.output_ports.model import (
        OutputPort,
    )


class DataProductVisibility(enum.Enum):
    HIDDEN = "hidden"
    DISCOVERABLE = "discoverable"


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
    visibility = mapped_column(
        SAEnum(
            DataProductVisibility,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=DataProductVisibility.DISCOVERABLE,
    )

    type_id: Mapped[UUID] = mapped_column(ForeignKey("data_product_types.id"))
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )

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
        secondary=tag_data_product_table,
        back_populates="data_products",
        lazy="raise",
        passive_deletes=True,
    )
    data_product_settings: Mapped[list["DataProductSettingValue"]] = relationship(
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.data_product_id",
        lazy="raise",
    )
    technical_assets: Mapped[list["TechnicalAsset"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    environments: Mapped[list["DataProductEnvironment"]] = relationship(
        cascade="all, delete-orphan",
        order_by="DataProductEnvironment.creation_date, DataProductEnvironment.environment_id",
        lazy="raise",
    )

    user_count = column_property(
        select(func.count(DataProductRoleAssignment.id))
        .where(DataProductRoleAssignment.data_product_id == id)
        .where(DataProductRoleAssignment.decision == DecisionStatus.APPROVED)
        .correlate_except(DataProductRoleAssignment)
        .scalar_subquery()
    )

    technical_asset_count = column_property(
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


class DataProductEnvironment(Base):
    __tablename__ = "data_product_environments"

    data_product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("data_products.id", ondelete="CASCADE"), primary_key=True
    )
    environment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("environments.id"), primary_key=True
    )
    creation_date: Mapped[datetime] = mapped_column(
        UTCDateTime(), server_default=utcnow()
    )
    environment: Mapped[Environment] = relationship(lazy="joined")


def ensure_data_product_exists(
    data_product_id: UUID, db: Session, **kwargs
) -> DataProduct:
    return ensure_exists(data_product_id, db, DataProduct, **kwargs)
