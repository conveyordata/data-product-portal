"""remove configuration type column

Revision ID: 3d6be1e9b5fa
Revises: 2b47064c5d10
Create Date: 2024-11-13 15:10:45.791325

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3d6be1e9b5fa"
down_revision: Union[str, None] = "2b47064c5d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("data_outputs", "configuration_type")


def downgrade() -> None:
    op.add_column("data_outputs", sa.Column("configuration_type", sa.String))
