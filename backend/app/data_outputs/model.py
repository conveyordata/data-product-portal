import uuid

from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, relationship

from app.data_outputs.data_output_types import DataOutputTypes
from app.data_outputs.schema import DataOutput as DataOutputSchema
from app.data_outputs.status import DataOutputStatus
from app.data_outputs_datasets.model import DataOutputDatasetAssociation
from app.data_products.model import DataProduct
from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM


def ensure_data_output_exists(data_output_id: UUID, db: Session) -> DataOutputSchema:
    return ensure_exists(data_output_id, db, DataOutput)


class DataOutput(Base, BaseORM):
    __tablename__ = "data_outputs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String)
    name = Column(String)
    description = Column(String)
    status: DataOutputStatus = Column(Enum(DataOutputStatus))
    owner_id: Mapped[UUID] = Column(ForeignKey("data_products.id"))
    owner: Mapped["DataProduct"] = relationship(back_populates="data_outputs")
    configuration_type: DataOutputTypes = Column(Enum(DataOutputTypes))
    configuration = Column(String)
    dataset_links: Mapped[list["DataOutputDatasetAssociation"]] = relationship(
        "DataOutputDatasetAssociation",
        back_populates="data_output",
        cascade="all, delete-orphan",
        order_by="DataOutputDatasetAssociation.status.desc()",
    )
