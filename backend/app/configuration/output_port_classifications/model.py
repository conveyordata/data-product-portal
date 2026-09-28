import uuid

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.data_products.output_ports.enums import OutputPortAccessType
from app.database.database import Base
from app.shared.model import BaseORM


class OutputPortClassification(Base, BaseORM):
    __tablename__ = "output_port_classifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    access_type: Mapped[OutputPortAccessType] = mapped_column(
        Enum(OutputPortAccessType, native_enum=False), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_output_port_classification_name"),
    )
