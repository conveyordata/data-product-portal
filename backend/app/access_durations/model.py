import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.abstract_data_product.type import AbstractDataProductType
from app.access_durations.enums import AccessDurationType
from app.database.database import Base
from app.shared.model import BaseORM


class AccessDuration(Base, BaseORM):
    __tablename__ = "access_durations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    abstract_data_product_type: Mapped[AbstractDataProductType] = mapped_column(
        SAEnum(
            AbstractDataProductType,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )
    access_duration_type: Mapped[AccessDurationType] = mapped_column(
        SAEnum(
            AccessDurationType,
            values_callable=lambda enum: [e.value for e in enum],
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )
    days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_default: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint(
            "abstract_data_product_type",
            "access_duration_type",
            name="uq_access_duration_type",
        ),
    )
