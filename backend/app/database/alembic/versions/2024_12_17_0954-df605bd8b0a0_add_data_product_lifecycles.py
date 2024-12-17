"""add data product lifecycles

Revision ID: df605bd8b0a0
Revises: 3d6be1e9b5fa
Create Date: 2024-12-17 09:54:50.828048

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "df605bd8b0a0"
down_revision: Union[str, None] = "3d6be1e9b5fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_product_lifecycles",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("data_product_lifecycles")
