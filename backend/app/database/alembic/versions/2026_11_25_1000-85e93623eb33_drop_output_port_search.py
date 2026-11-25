"""Drop Output Port search

Revision ID: 85e93623eb33
Revises: f89462ec4af6
Create Date: 2026-11-25 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "85e93623eb33"
down_revision: Union[str, None] = "f89462ec4af6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("idx_datasets_embeddings_hnsw", "datasets")
    op.drop_column("datasets", "embeddings")
    op.drop_index("idx_datasets_search_vector", "datasets")
    op.drop_column("datasets", "search_vector")


def downgrade() -> None:
    op.add_column("datasets", sa.Column("search_vector", postgresql.TSVECTOR))
    op.create_index(
        "idx_datasets_search_vector",
        "datasets",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )
    op.add_column("datasets", sa.Column("embeddings", Vector(384), nullable=True))
    op.execute(
        "CREATE INDEX idx_datasets_embeddings_hnsw ON datasets USING hnsw (embeddings vector_cosine_ops)"
    )
