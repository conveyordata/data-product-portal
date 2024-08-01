"""reintroduce context

Revision ID: fad6a9c64d60
Revises: 2e48ad16e9f7
Create Date: 2024-07-30 09:43:11.271634

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fad6a9c64d60"
down_revision: Union[str, None] = "2e48ad16e9f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("environments", sa.Column("context", sa.String))


def downgrade() -> None:
    op.drop_column("environments", "context")
