"""Add ephemeral data products

Revision ID: b8f2e1d4c9a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-14 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b8f2e1d4c9a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_products",
        sa.Column(
            "is_ephemeral",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )
    op.add_column(
        "data_products",
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "data_products",
        sa.Column("ttl_hours", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("data_products", "ttl_hours")
    op.drop_column("data_products", "expires_at")
    op.drop_column("data_products", "is_ephemeral")
