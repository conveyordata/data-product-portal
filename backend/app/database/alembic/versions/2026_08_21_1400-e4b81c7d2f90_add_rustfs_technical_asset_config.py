"""Add RustFS technical asset configuration table

Revision ID: e4b81c7d2f90
Revises: 44b3eff9ab38
Create Date: 2026-08-21 14:00:00.000000

"""

from typing import Sequence, Union

revision: str = "e4b81c7d2f90"
down_revision: Union[str, None] = "44b3eff9ab38"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The rustfs plugin's own versions/ now owns this table entirely.
    pass


def downgrade() -> None:
    pass
