import uuid

from sqlalchemy import Enum, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, Session, mapped_column

from app.data_products.output_ports.enums import OutputPortAccessFunction
from app.database.database import Base, ensure_exists
from app.shared.model import BaseORM


class OutputPortAccessType(Base, BaseORM):
    __tablename__ = "output_port_access_types"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False, default="")
    access_function: Mapped[OutputPortAccessFunction] = mapped_column(
        Enum(OutputPortAccessFunction, native_enum=False), nullable=False
    )

    __table_args__ = (UniqueConstraint("name", name="uq_output_port_access_type_name"),)


def ensure_output_port_access_type_exists(
    access_type_id: uuid.UUID, db: Session
) -> OutputPortAccessType:
    return ensure_exists(access_type_id, db, OutputPortAccessType)
