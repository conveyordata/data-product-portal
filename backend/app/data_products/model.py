import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_product_memberships.model import DataProductMembership
from app.data_products.schema import DataProduct as DataProductSchema
from app.data_products.status import DataProductStatus
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM, utcnow
from app.tags.model import Tag

if TYPE_CHECKING:
    from app.business_areas.model import BusinessArea
    from app.data_outputs.model import DataOutput
    from app.data_product_types.model import DataProductType

tag_data_product_table = Table(
    "tags_data_products",
    Base.metadata,
    Column("data_product_id", ForeignKey("data_products.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


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
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_data_product_table,
        cascade="all, delete-orphan",
        single_parent=True,
    )
    type_id: Mapped[UUID] = mapped_column(ForeignKey("data_product_types.id"))
    type: Mapped["DataProductType"] = relationship(back_populates="data_products")
    business_area_id: Mapped[UUID] = Column(ForeignKey("business_areas.id"))
    business_area: Mapped["BusinessArea"] = relationship(back_populates="data_products")
    data_outputs: Mapped[list["DataOutput"]] = relationship(
        "DataOutput",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
