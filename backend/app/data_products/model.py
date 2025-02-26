import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_product_memberships.model import DataProductMembership
from app.data_product_settings.model import DataProductSettingValue
from app.data_products.schema import DataProduct as DataProductSchema
from app.data_products.status import DataProductStatus
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM
from app.tags.model import Tag, tag_data_product_table

if TYPE_CHECKING:
    from app.data_outputs.model import DataOutput
    from app.data_product_lifecycles.model import DataProductLifecycle
    from app.data_product_types.model import DataProductType
    from app.domains.model import Domain


def ensure_data_product_exists(data_product_id: UUID, db: Session) -> DataProductSchema:
    return ensure_exists(data_product_id, db, DataProduct)


class DataProduct(Base, BaseORM):
    __tablename__ = "data_products"
    id = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    external_id = Column(String)
    description = Column(String)
    about = Column(String)
    memberships: Mapped[list["DataProductMembership"]] = relationship(
        "DataProductMembership",
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductMembership.status, "
        "DataProductMembership.requested_on, "
        "DataProductMembership.role",
    )
    status: DataProductStatus = Column(
        Enum(DataProductStatus), default=DataProductStatus.ACTIVE
    )
    dataset_links: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductDatasetAssociation.status.desc()",
    )
    tags: Mapped[list[Tag]] = relationship(secondary=tag_data_product_table)
    data_product_settings: Mapped[list["DataProductSettingValue"]] = relationship(
        "DataProductSettingValue",
        back_populates="data_product",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.data_product_id",
    )
    type_id: Mapped[UUID] = mapped_column(ForeignKey("data_product_types.id"))
    type: Mapped["DataProductType"] = relationship(back_populates="data_products")
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )
    lifecycle: Mapped["DataProductLifecycle"] = relationship(
        back_populates="data_products"
    )
    domain_id: Mapped[UUID] = Column(ForeignKey("domains.id"))
    domain: Mapped["Domain"] = relationship(back_populates="data_products")
    data_outputs: Mapped[list["DataOutput"]] = relationship(
        "DataOutput",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
