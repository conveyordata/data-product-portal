"""Add user admin expiry

Revision ID: 01dd943b2702
Revises: 749165238a8f
Create Date: 2025-11-19 16:30:46.215932

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "01dd943b2702"
down_revision: Union[str, None] = "749165238a8f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("admin_expiry", sa.DateTime(timezone=False), nullable=True),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_column("users", "admin_expiry")
