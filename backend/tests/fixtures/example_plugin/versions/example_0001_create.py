"""Create example_plugin_assets

Revision ID: example_0001_create
Revises:
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "example_0001_create"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "example_plugin_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("example_plugin_assets")
