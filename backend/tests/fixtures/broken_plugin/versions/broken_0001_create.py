"""Read a core column that core no longer has

Revision ID: broken_0001_create
Revises:
"""

from alembic import op

revision = "broken_0001_create"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("SELECT renamed_away FROM platform_services")


def downgrade() -> None:
    pass
