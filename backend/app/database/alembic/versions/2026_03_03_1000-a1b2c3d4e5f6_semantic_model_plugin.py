"""Semantic model output port plugin

Revision ID: a1b2c3d4e5f6
Revises: 491c8783a7bc
Create Date: 2026-03-03 10:00:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "491c8783a7bc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The osi_sem_model plugin's own versions/ now owns this table entirely.
    pass


def downgrade() -> None:
    pass
