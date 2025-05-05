"""Merge 2a5 and 269

Revision ID: aeffee7f1029
Revises: 2a58b7ce3cea, 269e6dbd565c
Create Date: 2025-03-25 15:42:02.597549

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "aeffee7f1029"
down_revision: Sequence[Union[str, None]] = ("2a58b7ce3cea", "269e6dbd565c")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
