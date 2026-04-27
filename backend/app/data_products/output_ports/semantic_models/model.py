import enum
import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class SemanticModelFormat(str, enum.Enum):
    MetricsFlow = "MetricsFlow"
    OpenSemanticInterchange = "OpenSemanticInterchange"


class OutputPortSemanticModel(Base):
    __tablename__ = "output_port_semantic_models"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    output_port_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[SemanticModelFormat] = mapped_column(
        SAEnum(SemanticModelFormat), nullable=False
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
