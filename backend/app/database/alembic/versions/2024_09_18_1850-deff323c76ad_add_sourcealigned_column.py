"""add sourceAligned column

Revision ID: deff323c76ad
Revises: 0ec371fe987b
Create Date: 2024-09-18 18:50:36.074437

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "deff323c76ad"
down_revision: Union[str, None] = "0ec371fe987b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_outputs", sa.Column("sourceAligned", sa.Boolean))


def downgrade() -> None:
    op.drop_column("data_outputs", sa.Column("sourceAligned", sa.Boolean))
