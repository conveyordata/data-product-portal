"""Drop the Casbin consumer links

Revision ID: 8d92ae03b40d
Revises: 5c7e2a91b4d3
Create Date: 2026-11-16 22:46:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "8d92ae03b40d"
down_revision: Union[str, None] = "5c7e2a91b4d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The Casbin adapter creates casbin_rule at runtime, so a fresh database has none yet.
    if sa.inspect(op.get_bind()).has_table("casbin_rule"):
        op.execute("DELETE FROM casbin_rule WHERE ptype = 'g4'")


def downgrade() -> None:
    # The links can't be restored; the older release's startup sync rebuilds them.
    pass
