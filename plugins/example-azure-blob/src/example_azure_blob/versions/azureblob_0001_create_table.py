"""Create azure_blob_plugin_assets

Revision ID: azureblob_0001_create_table
Revises:
Create Date: 2026-09-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "azureblob_0001_create_table"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "azure_blob_plugin_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("technical_asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("container_name", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("azure_blob_plugin_assets")
