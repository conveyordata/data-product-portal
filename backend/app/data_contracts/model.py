import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_contracts.column.model import Column as SchemaColumn
    from app.data_contracts.service_level_objective.model import ServiceLevelObjective


class DataContract(Base, BaseORM):
    __tablename__ = "data_contracts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_output_id: Mapped[UUID] = mapped_column(ForeignKey("data_outputs.id"))
    table = Column(String)
    description = Column(String)
    checks = Column(String)

    columns: Mapped[list["SchemaColumn"]] = relationship(
        "Column", back_populates="data_contract", cascade="all, delete-orphan"
    )
    service_level_objectives: Mapped[list["ServiceLevelObjective"]] = relationship(
        "ServiceLevelObjective",
        back_populates="data_contract",
        cascade="all, delete-orphan",
    )
