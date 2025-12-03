"""create dataset_query_stats_daily_table

Revision ID: 58c7d09c5798
Revises: 0f590c0c9b20
Create Date: 2025-11-20 10:56:42.720373

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "58c7d09c5798"
down_revision: Union[str, None] = "249eae21bcac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_query_stats_daily",
        sa.Column("date", sa.Date(), nullable=False, primary_key=True),
        sa.Column(
            "dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("datasets.id"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "consumer_data_product_id",
            UUID(as_uuid=True),
            sa.ForeignKey("data_products.id"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column("query_count", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("date", "dataset_id", "consumer_data_product_id"),
    )
    op.create_index(
        "idx_dataset_query_stats_daily_date",
        "dataset_query_stats_daily",
        ["date"],
    )
    op.create_index(
        "idx_dataset_query_stats_daily_dataset_id",
        "dataset_query_stats_daily",
        ["dataset_id"],
    )
    op.create_index(
        "idx_dataset_query_stats_daily_consumer_data_product_id",
        "dataset_query_stats_daily",
        ["consumer_data_product_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "idx_dataset_query_stats_daily_date",
        table_name="dataset_query_stats_daily",
    )
    op.drop_index(
        "idx_dataset_query_stats_daily_consumer_data_product_id",
        table_name="dataset_query_stats_daily",
    )
    op.drop_index(
        "idx_dataset_query_stats_daily_dataset_id",
        table_name="dataset_query_stats_daily",
    )
    op.drop_table("dataset_query_stats_daily")
