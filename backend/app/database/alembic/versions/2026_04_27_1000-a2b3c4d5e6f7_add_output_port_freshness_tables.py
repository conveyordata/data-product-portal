"""add output port freshness tables

Revision ID: a2b3c4d5e6f7
Revises: 1b4af17b29f7
Create Date: 2026-04-27 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.shared.model import utcnow

revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, None] = "1b4af17b29f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "output_port_freshness_slos",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("deadline_time", sa.Time(timezone=False), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=utcnow(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=utcnow(),
        ),
        sa.UniqueConstraint("output_port_id"),
    )

    op.create_table(
        "output_port_freshness_observations",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "last_refreshed_at", sa.DateTime(timezone=True), nullable=False, index=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=utcnow(),
        ),
    )


def downgrade() -> None:
    op.drop_table("output_port_freshness_observations")
    op.drop_table("output_port_freshness_slos")
