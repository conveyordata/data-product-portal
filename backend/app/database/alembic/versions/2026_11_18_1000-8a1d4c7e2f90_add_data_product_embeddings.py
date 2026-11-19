"""Add data product embeddings

Revision ID: 8a1d4c7e2f90
Revises: 5c7e2a91b4d3
Create Date: 2026-11-18 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy import orm

from app.data_products.service import DataProductService

# revision identifiers, used by Alembic.
revision: str = "8a1d4c7e2f90"
down_revision: Union[str, None] = "5c7e2a91b4d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_products", sa.Column("embeddings", Vector(384), nullable=True))
    op.execute(
        "CREATE INDEX idx_data_products_embeddings_hnsw ON data_products USING hnsw (embeddings vector_cosine_ops)"
    )
    session = orm.Session(bind=op.get_bind())
    DataProductService(session).recalculate_search_for_all_data_products()


def downgrade() -> None:
    op.drop_index("idx_data_products_embeddings_hnsw", "data_products")
    op.drop_column("data_products", "embeddings")
