"""Added admin flag to users

Revision ID: 4e61079eaf16
Revises: 4c40a4ff5a7f
Create Date: 2024-07-16 12:38:37.382829

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4e61079eaf16"
down_revision: Union[str, None] = "4c40a4ff5a7f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("users", "is_admin")
