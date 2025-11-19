"""Add user can become admin

Revision ID: 749165238a8f
Revises: 0f590c0c9b20
Create Date: 2025-11-19 13:38:28.574326

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "749165238a8f"
down_revision: Union[str, None] = "0f590c0c9b20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add can_become_admin column to user table
    op.add_column(
        "users",
        sa.Column(
            "can_become_admin", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )


def downgrade() -> None:
    # Remove can_become_admin column from user table
    op.drop_column("users", "can_become_admin")
