"""Baseline for the S3 technical asset configuration table.

The table already exists in every deployment that ran the core migrations from
before S3 became a plugin, so this revision creates it only when it is missing.
From here on the table belongs to this plugin's own migration history.

Revision ID: s3_0001_baseline
Revises:
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "s3_0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "s3_technical_asset_configurations"


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
        sa.Column("bucket", sa.String(), nullable=True),
        sa.Column("suffix", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table(TABLE)
