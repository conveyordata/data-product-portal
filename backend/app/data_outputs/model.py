import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, relationship

from app.data_outputs.schema import DataOutput as DataOutputSchema
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.model import DataOutputDatasetAssociation

if TYPE_CHECKING:
    from app.data_products.model import DataProduct
    from app.data_outputs.base_model import BaseDataOutputConfiguration

from app.database.database import Base, ensure_exists
from app.platform_services.schema import PlatformService
from app.platforms.schema import Platform
from app.shared.model import BaseORM, utcnow
from app.tags.model import Tag

tag_data_output_table = Table(
    "tags_data_outputs",
    Base.metadata,
    Column("data_output_id", ForeignKey("data_outputs.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


def ensure_data_output_exists(data_output_id: UUID, db: Session) -> DataOutputSchema:
    return ensure_exists(data_output_id, db, DataOutput)


class DataOutput(Base, BaseORM):
    __tablename__ = "data_outputs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String)
    name = Column(String)
    description = Column(String)
    status: DataOutputStatus = Column(Enum(DataOutputStatus))
    platform_id: Mapped[UUID] = Column(ForeignKey("platforms.id"))
    service_id: Mapped[UUID] = Column(ForeignKey("platform_services.id"))
    owner_id: Mapped[UUID] = Column(ForeignKey("data_products.id"))
    owner: Mapped["DataProduct"] = relationship(back_populates="data_outputs")
    configuration: Mapped["BaseDataOutputConfiguration"] = relationship()
    configuration_id: Mapped[UUID] = Column(ForeignKey("data_output_configurations.id"))
    dataset_links: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        back_populates="data_output",
        cascade="all, delete-orphan",
        order_by="DataOutputDatasetAssociation.status.desc()",
    )
    sourceAligned = Column(Boolean)

    platform: Mapped["Platform"] = relationship()
    service: Mapped["PlatformService"] = relationship()
    tags: Mapped[list[Tag]] = relationship(secondary=tag_data_output_table)
