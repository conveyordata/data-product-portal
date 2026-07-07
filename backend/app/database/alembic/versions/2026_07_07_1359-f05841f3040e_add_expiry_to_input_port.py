"""add expiry to input port

Revision ID: f05841f3040e
Revises: 56e4e97d7294
Create Date: 2026-07-07 13:59:11.988166

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f05841f3040e"
down_revision: Union[str, None] = "56e4e97d7294"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "input_ports",
        sa.Column("requested_duration_days", sa.Integer(), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("expires_on", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("renewed_on", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("total_range_start", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("total_range_end", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "input_ports",
        sa.Column("expired_on", sa.DateTime(timezone=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("input_ports", "total_range_end")
    op.drop_column("input_ports", "total_range_start")
    op.drop_column("input_ports", "expires_on")
    op.drop_column("input_ports", "requested_duration_days")
    op.drop_column("input_ports", "renewed_on")
    op.drop_column("input_ports", "expired_on")
