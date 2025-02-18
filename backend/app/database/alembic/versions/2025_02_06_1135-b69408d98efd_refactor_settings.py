"""refactor settings

Revision ID: b69408d98efd
Revises: c5730551b99e
Create Date: 2025-02-06 11:35:13.845665

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b69408d98efd"
down_revision: Union[str, None] = "c5730551b99e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("data_product_settings", "divider", new_column_name="category")


def downgrade() -> None:
    op.alter_column("data_product_settings", "category", new_column_name="divider")
