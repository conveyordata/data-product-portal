"""Create dataset curated queries

Revision ID: b3f7df8cf884
Revises: 0f590c0c9b20
Create Date: 2025-11-25 10:15:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "b3f7df8cf884"
down_revision: Union[str, None] = "0f590c0c9b20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_curated_queries",
        sa.Column(
            "curated_query_id",
            sa.UUID,
            primary_key=True,
            nullable=False,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=utcnow(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
            onupdate=utcnow(),
        ),
    )
    op.create_index(
        "ix_dataset_curated_queries_output_port_id",
        "dataset_curated_queries",
        ["output_port_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dataset_curated_queries_output_port_id",
        table_name="dataset_curated_queries",
    )
    op.drop_table("dataset_curated_queries")
