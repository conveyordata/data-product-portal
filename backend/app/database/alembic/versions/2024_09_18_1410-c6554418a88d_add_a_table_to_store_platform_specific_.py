"""Add a table to store platform specific config

Revision ID: c6554418a88d
Revises: a60896a3b95a
Create Date: 2024-09-18 14:10:36.738932

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "c6554418a88d"
down_revision: Union[str, None] = "a60896a3b95a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "env_platform_configs",
        sa.Column(
            "id", sa.UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")
        ),
        sa.Column(
            "environment_id",
            sa.UUID,
            sa.ForeignKey("environments.id", ondelete="CASCADE"),
        ),
        sa.Column("platform_id", sa.UUID, sa.ForeignKey("platforms.id")),
        sa.Column("config", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("env_platform_configs")
