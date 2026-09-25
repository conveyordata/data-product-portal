"""add exploration event reference entity

Revision ID: abd4229ea6af
Revises: 18fb80f18c7d
Create Date: 2026-09-25 16:14:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "abd4229ea6af"
down_revision: Union[str, None] = "18fb80f18c7d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.bulk_insert(
        sa.table("event_reference_entities", sa.column("key", sa.String)),
        [{"key": "EXPLORATION"}],
    )


def downgrade() -> None:
    op.execute("DELETE FROM event_reference_entities WHERE key = 'EXPLORATION'")
