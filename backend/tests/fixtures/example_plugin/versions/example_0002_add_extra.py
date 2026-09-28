"""Add extra to example_plugin_assets

Revision ID: example_0002_add_extra
Revises: example_0001_create
"""

import sqlalchemy as sa
from alembic import op

revision = "example_0002_add_extra"
down_revision = "example_0001_create"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("example_plugin_assets", sa.Column("extra", sa.String()))


def downgrade() -> None:
    op.drop_column("example_plugin_assets", "extra")
