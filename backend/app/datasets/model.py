import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_product_lifecycles.model import DataProductLifecycle
from app.data_products_datasets.model import DataProductDatasetAssociation
from app.database.database import Base, ensure_exists
from app.datasets.enums import DatasetAccessType
from app.datasets.status import DatasetStatus
from app.domains.model import Domain
from app.role_assignments.enums import DecisionStatus
from app.shared.model import BaseORM, utcnow
from app.tags.model import Tag, tag_dataset_table

if TYPE_CHECKING:
    from app.data_product_settings.model import DataProductSettingValue
    from app.users.model import User

datasets_owner_table = Table(
    "datasets_owners",
    Base.metadata,
    Column("dataset_id", ForeignKey("datasets.id")),
    Column("users_id", ForeignKey("users.id")),
    Column("created_on", DateTime(timezone=False), server_default=utcnow()),
    Column("updated_on", DateTime(timezone=False), onupdate=utcnow()),
)


class Dataset(Base, BaseORM):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    namespace = Column(String)
    name = Column(String)
    description = Column(String)
    about = Column(String)
    access_type = Column(Enum(DatasetAccessType), default=DatasetAccessType.PUBLIC)
    status: DatasetStatus = Column(Enum(DatasetStatus), default=DatasetStatus.ACTIVE)

    # Foreign keys
    lifecycle_id: Mapped[UUID] = mapped_column(
        ForeignKey("data_product_lifecycles.id", ondelete="SET NULL")
    )
    domain_id: Mapped[UUID] = Column(ForeignKey("domains.id"))

    # Relationships
    owners: Mapped[list["User"]] = relationship(
        secondary=datasets_owner_table, back_populates="owned_datasets", lazy="joined"
    )
    data_product_links: Mapped[list["DataProductDatasetAssociation"]] = relationship(
        "DataProductDatasetAssociation",
        back_populates="dataset",
        order_by="DataProductDatasetAssociation.status.desc()",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    data_output_links: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        back_populates="dataset",
        order_by="DataOutputDatasetAssociation.status.desc()",
        cascade="all, delete-orphan",
        lazy="raise",
    )
    tags: Mapped[list[Tag]] = relationship(
        secondary=tag_dataset_table, back_populates="datasets", lazy="joined"
    )
    data_product_settings: Mapped[list["DataProductSettingValue"]] = relationship(
        "DataProductSettingValue",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="DataProductSettingValue.dataset_id",
        lazy="joined",
    )
    lifecycle: Mapped["DataProductLifecycle"] = relationship(
        back_populates="datasets", lazy="joined"
    )
    domain: Mapped["Domain"] = relationship(back_populates="datasets", lazy="joined")

    @property
    def data_product_count(self) -> int:
        accepted_product_links = [
            link
            for link in self.data_product_links
            if link.status == DecisionStatus.APPROVED
        ]
        return len(accepted_product_links)

    def isVisibleToUser(self, user: "User"):
        if (
            self.access_type != DatasetAccessType.PRIVATE
            or user.is_admin
            or user in self.owners
        ):
            return True

        consuming_data_products = {
            link.data_product
            for link in self.data_product_links
            if link.status == DecisionStatus.APPROVED
        }

        user_data_products = {
            membership.data_product
            for membership in user.data_product_memberships
            if membership.status == DecisionStatus.APPROVED
        }

        return bool(consuming_data_products & user_data_products)


def ensure_dataset_exists(dataset_id: UUID, db: Session, **kwargs) -> Dataset:
    return ensure_exists(dataset_id, db, Dataset, **kwargs)
