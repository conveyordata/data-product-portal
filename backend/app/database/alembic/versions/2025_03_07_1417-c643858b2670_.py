"""empty message

Revision ID: c643858b2670
Revises: 2a58b7ce3cea, 269e6dbd565c
Create Date: 2025-03-07 14:17:14.771393

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c643858b2670'
down_revision: Union[str, None] = ('2a58b7ce3cea', '269e6dbd565c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
