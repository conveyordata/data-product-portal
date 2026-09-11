"""Add plugin_key to data_outputs

Revision ID: f3a1c9d4b6e2
Revises: ad035abcf21d
Create Date: 2026-09-11 09:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f3a1c9d4b6e2"
down_revision: Union[str, None] = "ad035abcf21d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("data_outputs", sa.Column("plugin_key", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("data_outputs", "plugin_key")
