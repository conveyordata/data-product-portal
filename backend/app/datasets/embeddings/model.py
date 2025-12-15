import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class DatasetEmbedding(Base):
    __tablename__ = "dataset_embeddings"
    # UUID Column: Primary Key, generates a new UUID by default
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Vector Column: Dimension of 1024
    embeddings = mapped_column(Vector(1024))
