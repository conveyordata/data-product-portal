"""Add owner to exploration

Revision ID: 8b489330a188
Revises: b1b690376725
Create Date: 2026-04-27 11:19:25.042862

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8b489330a188"
down_revision: Union[str, None] = "b1b690376725"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # We clean up all explorations, explorations created before this had no owner and will not be visible
    op.execute("DELETE FROM explorations")
    op.add_column(
        "explorations",
        sa.Column("owner_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column(
        "explorations",
        "owner_id",
    )
