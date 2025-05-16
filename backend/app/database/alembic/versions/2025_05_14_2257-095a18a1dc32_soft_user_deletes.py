"""soft user deletes

Revision ID: 095a18a1dc32
Revises: 7727032896e7
Create Date: 2025-05-14 22:57:52.142566

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '095a18a1dc32'
down_revision: Union[str, None] = '7727032896e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    op.drop_column('users', 'is_deleted')
