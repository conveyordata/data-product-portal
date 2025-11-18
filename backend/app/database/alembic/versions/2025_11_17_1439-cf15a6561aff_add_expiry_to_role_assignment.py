"""Add expiry to role assignment

Revision ID: cf15a6561aff
Revises: 0f590c0c9b20
Create Date: 2025-11-17 14:39:52.440661

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cf15a6561aff"
down_revision: Union[str, None] = "0f590c0c9b20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "role_assignments_global",
        sa.Column("expiry", sa.DateTime(timezone=False), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("role_assignments_global", "expiry")
