"""Create other_plugin_assets

Revision ID: other_0001_create
Revises:
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "other_0001_create"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "other_plugin_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("other_plugin_assets")
