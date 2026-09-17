"""Baseline for the Azure Blob technical asset configuration table.

The table already exists in every deployment that ran the core migrations
from before Azure Blob became a plugin, so this revision creates it only when
it is missing. From here on the table belongs to this plugin's own migration
history.

Revision ID: azure_blob_0001_baseline
Revises:
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision: str = "azure_blob_0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = "azure_blob_technical_asset_configurations"


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
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("container_name", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_table(TABLE)
