"""remove consumer casbin links

Revision ID: 9b6e2f4c1a7d
Revises: 3f1c2b7a9d4e
Create Date: 2026-10-06 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9b6e2f4c1a7d"
down_revision: Union[str, None] = "3f1c2b7a9d4e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("casbin_rule"):
        op.execute("DELETE FROM casbin_rule WHERE ptype = 'g4'")


def downgrade() -> None:
    pass
