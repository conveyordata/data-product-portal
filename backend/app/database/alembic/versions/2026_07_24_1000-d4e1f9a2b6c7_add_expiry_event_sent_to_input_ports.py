"""Add expiry_event_sent to input ports

Revision ID: d4e1f9a2b6c7
Revises: c3d8a1f56e42
Create Date: 2026-07-24 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e1f9a2b6c7"
down_revision: Union[str, None] = "c3d8a1f56e42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "input_ports",
        sa.Column(
            "expiry_event_sent",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("input_ports", "expiry_event_sent")
