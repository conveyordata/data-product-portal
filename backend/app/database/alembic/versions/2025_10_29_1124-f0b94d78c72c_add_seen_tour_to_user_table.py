"""Add seen_tour to user table

Revision ID: f0b94d78c72c
Revises: d56d796fb20d
Create Date: 2025-10-29 11:24:36.562990

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f0b94d78c72c"
down_revision: Union[str, None] = "d56d796fb20d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add has_seen_tour column to user table
    op.add_column(
        "users",
        sa.Column(
            "has_seen_tour", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )


def downgrade() -> None:
    # Remove has_seen_tour column from user table
    op.drop_column("users", "has_seen_tour")
