"""Remove admin field

Revision ID: eb57869c9840
Revises: 93e7f3907ca8
Create Date: 2025-05-28 17:46:03.575686

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "eb57869c9840"
down_revision: Union[str, None] = "93e7f3907ca8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("user", "admin")


def downgrade() -> None:
    op.add_column(
        "user", sa.Column("admin", sa.BOOLEAN, server_default="false", nullable=False)
    )
