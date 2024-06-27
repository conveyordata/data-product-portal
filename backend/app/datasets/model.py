import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, String, ForeignKey, Table, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, Session

from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import Base, ensure_exists
from app.datasets.enums import DatasetAccessType
from app.datasets.schema import Dataset as DatasetSchema
from app.datasets.status import DatasetStatus
from app.shared.model import BaseORM, utcnow
from app.tags.model import Tag

if TYPE_CHECKING:
    from app.business_areas.model import BusinessArea
    from app.users.model import User


tag_dataset_table = Table(
    "tags_datasets",
    Base.metadata,
    Column("dataset_id", ForeignKey("datasets.id")),
    Column("tag_id", ForeignKey("tags.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)
datasets_owner_table = Table(
    "datasets_owners",
    Base.metadata,
    Column("dataset_id", ForeignKey("datasets.id")),
    Column("users_id", ForeignKey("users.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


def ensure_dataset_exists(dataset_id: UUID, db: Session) -> DatasetSchema:
    return ensure_exists(dataset_id, db, Dataset)


class Dataset(Base, BaseORM):
    __tablename__ = "datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String)
    name = Column(String)
    description = Column(String)
    about = Column(String)
    access_type = Column(Enum(DatasetAccessType), default=DatasetAccessType.PUBLIC)
    owners: Mapped[list["User"]] = relationship(
        secondary=datasets_owner_table, back_populates="owned_datasets"
    )
    status: DatasetStatus = Column(Enum(DatasetStatus), default=DatasetStatus.PENDING)
    data_product_links: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        back_populates="dataset",
        order_by="DataProductDatasetAssociation.status.desc()",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_dataset_table, cascade="all, delete-orphan", single_parent=True
    )
    business_area_id: Mapped[UUID] = Column(ForeignKey("business_areas.id"))
    business_area: Mapped["BusinessArea"] = relationship(back_populates="datasets")
