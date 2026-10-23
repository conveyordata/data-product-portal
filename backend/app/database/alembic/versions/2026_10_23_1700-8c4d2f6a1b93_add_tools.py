"""Add tools and their per-environment overrides

Revision ID: 8c4d2f6a1b93
Revises: 5b1e7c2d9a40
Create Date: 2026-10-23 17:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

revision: str = "8c4d2f6a1b93"
down_revision: Union[str, None] = "5b1e7c2d9a40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tools",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=False),
        sa.Column(
            "data_product_id",
            sa.UUID,
            sa.ForeignKey("data_products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform_key", sa.String, nullable=False),
        sa.Column("tool_type", sa.String, nullable=False),
        sa.Column("base_values", postgresql.JSONB, nullable=False),
        sa.Column("created_on", sa.DateTime, server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime, onupdate=utcnow()),
    )
    op.create_table(
        "tool_environment_overrides",
        sa.Column(
            "tool_id",
            sa.UUID,
            sa.ForeignKey("tools.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "environment_id",
            sa.UUID,
            sa.ForeignKey("environments.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("values", postgresql.JSONB, nullable=False),
        sa.Column("created_on", sa.DateTime, server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime, onupdate=utcnow()),
    )


def downgrade() -> None:
    op.drop_table("tool_environment_overrides")
    op.drop_table("tools")
