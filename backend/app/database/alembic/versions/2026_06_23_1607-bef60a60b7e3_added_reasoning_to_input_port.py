"""Added reasoning to input port

Revision ID: bef60a60b7e3
Revises: ecaa71141f4c
Create Date: 2026-06-23 16:07:40.773158

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bef60a60b7e3"
down_revision: Union[str, None] = "ecaa71141f4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "input_ports",
        sa.Column("reasoning", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("input_ports", "reasoning")
