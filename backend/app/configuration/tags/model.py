import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, Session, relationship

from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM, utcnow

if TYPE_CHECKING:
    from app.data_products.model import DataProduct
    from app.data_products.output_ports.model import OutputPort
    from app.data_products.technical_assets.model import TechnicalAsset


tag_data_product_table = Table(
    "tags_data_products",
    Base.metadata,
    Column("data_product_id", ForeignKey("data_products.id", ondelete="CASCADE")),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)

tag_output_port_table = Table(
    "tags_datasets",
    Base.metadata,
    Column("dataset_id", ForeignKey("datasets.id", ondelete="CASCADE")),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)

tag_technical_asset_table = Table(
    "tags_data_outputs",
    Base.metadata,
    Column("data_output_id", ForeignKey("data_outputs.id", ondelete="CASCADE")),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


class Tag(Base, BaseORM):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    value = Column(String)

    # Relationships
    output_ports: Mapped[list["OutputPort"]] = relationship(
        secondary=tag_output_port_table,
        lazy="raise",
        back_populates="tags",
        passive_deletes=True,
    )
    data_products: Mapped[list["DataProduct"]] = relationship(
        secondary=tag_data_product_table,
        lazy="raise",
        back_populates="tags",
        passive_deletes=True,
    )
    technical_assets: Mapped[list["TechnicalAsset"]] = relationship(
        secondary=tag_technical_asset_table,
        lazy="raise",
        back_populates="tags",
        passive_deletes=True,
    )


def ensure_tag_exists(tag_id: UUID, db: Session) -> Tag:
    return ensure_exists(tag_id, db, Tag)
