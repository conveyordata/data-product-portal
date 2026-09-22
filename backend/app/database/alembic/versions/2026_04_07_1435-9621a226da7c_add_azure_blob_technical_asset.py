"""Add azure blob technical asset

Revision ID: 9621a226da7c
Revises: 72cc4963a251
Create Date: 2026-04-07 14:35:04.012802

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "9621a226da7c"
down_revision: Union[str, None] = "72cc4963a251"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The azure_blob plugin's own versions/ now owns this table entirely.
    pass


def downgrade() -> None:
    pass
