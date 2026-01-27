"""Add output-port embeddings

Revision ID: c3fecd278d0c
Revises: dbe6fbe45eef
Create Date: 2026-01-27 10:19:31.581396

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "c3fecd278d0c"
down_revision: Union[str, None] = "dbe6fbe45eef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column("datasets", sa.Column("embeddings", Vector(384), nullable=True))
    op.execute(
        "CREATE INDEX idx_datasets_embeddings_hnsw ON datasets USING hnsw (embeddings vector_cosine_ops)"
    )


def downgrade() -> None:
    op.drop_index("idx_datasets_embeddings_hnsw", "datasets")
    op.drop_column("datasets", "embeddings")
