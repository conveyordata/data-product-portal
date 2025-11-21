"""Add justification to access requests

Revision ID: 0f590c0c9b20
Revises: f0b94d78c72c
Create Date: 2025-11-03 10:08:22.607641

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0f590c0c9b20"
down_revision: Union[str, None] = "f0b94d78c72c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "data_products_datasets",
        sa.Column(
            "justification",
            sa.Text(),
            nullable=False,
            server_default="No justification provided (migration)",
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "data_products_datasets",
        "justification",
    )
