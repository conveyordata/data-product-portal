"""Baseline for the Glue technical asset configuration table.

The table already exists in every deployment that ran the core migrations
from before Glue became a plugin, so this revision creates it only when it is
missing. From here on the table belongs to this plugin's own migration
history.

Revision ID: glue_0001_baseline
Revises:
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision: str = "glue_0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "glue_technical_asset_configurations"


def upgrade() -> None:
    if TABLE in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        TABLE,
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("database", sa.String(), nullable=True),
        sa.Column("database_suffix", sa.String(), nullable=True),
        sa.Column("table", sa.String(), nullable=True),
        sa.Column("bucket_identifier", sa.String(), nullable=True),
        sa.Column("database_path", sa.String(), nullable=True),
        sa.Column("table_path", sa.String(), nullable=True),
        sa.Column("access_granularity", sa.String(), nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_table(TABLE)
