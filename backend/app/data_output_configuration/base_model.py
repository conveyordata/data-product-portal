import uuid

from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.data_output_configuration.data_output_types import DataOutputTypes
from app.database.database import Base
from app.shared.model import BaseORM


class BaseDataOutputConfiguration(Base, BaseORM):
    __tablename__ = "data_output_configurations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    configuration_type: Mapped[DataOutputTypes] = Column(Enum(DataOutputTypes))

    __mapper_args__ = {
        "polymorphic_on": "configuration_type",
        "polymorphic_identity": "data_output",
    }
