import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, relationship

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM, utcnow

if TYPE_CHECKING:
    from app.data_outputs.model import DataOutput
    from app.data_products.model import DataProduct
    from app.datasets.model import Dataset


tag_data_product_table = Table(
    "tags_data_products",
    Base.metadata,
    Column("data_product_id", ForeignKey("data_products.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)

tag_dataset_table = Table(
    "tags_datasets",
    Base.metadata,
    Column("dataset_id", ForeignKey("datasets.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)

tag_data_output_table = Table(
    "tags_data_outputs",
    Base.metadata,
    Column("data_output_id", ForeignKey("data_outputs.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


class Tag(Base, BaseORM):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String)

    # Relationships
    datasets: Mapped[list["Dataset"]] = relationship(
        secondary=tag_dataset_table, lazy="raise", back_populates="tags"
    )
    data_products: Mapped[list["DataProduct"]] = relationship(
        secondary=tag_data_product_table, lazy="raise", back_populates="tags"
    )
    data_outputs: Mapped[list["DataOutput"]] = relationship(
        secondary=tag_data_output_table, lazy="raise", back_populates="tags"
    )


def ensure_tag_exists(tag_id: UUID, db: Session) -> Tag:
    return ensure_exists(tag_id, db, Tag)
