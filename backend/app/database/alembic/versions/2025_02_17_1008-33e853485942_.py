"""empty message

Revision ID: 33e853485942
Revises: d0130a2f2f21, b69408d98efd
Create Date: 2025-02-17 10:08:41.317039

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "33e853485942"
down_revision: Union[tuple[str, str], None] = ("d0130a2f2f21", "b69408d98efd")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
