"""add usage column

Revision ID: 0358e660a680
Revises: f967668dbf54
Create Date: 2025-07-29 10:24:27.550560

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0358e660a680"
down_revision: Union[str, None] = "f967668dbf54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_products", sa.Column("usage", sa.String(), nullable=True))
    op.add_column("datasets", sa.Column("usage", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("data_products", "usage")
    op.drop_column("datasets", "usage")
