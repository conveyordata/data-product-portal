import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column as SQLColumn
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.shared.model import BaseORM

if TYPE_CHECKING:
    from app.data_contracts.model import DataContract as DataContractModel


class Column(Base, BaseORM):
    __tablename__ = "columns"
    id = SQLColumn(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_contract_id: Mapped[UUID] = mapped_column(ForeignKey("data_contracts.id"))
    name = SQLColumn(String)
    description = SQLColumn(String)
    data_type = SQLColumn(String)
    checks = SQLColumn(ARRAY(String))

    data_contract: Mapped["DataContractModel"] = relationship(
        "DataContract", back_populates="columns"
    )
