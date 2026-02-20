"""Dataset index on name

Revision ID: bb31223f935e
Revises: 2bac081ab9d0
Create Date: 2026-02-19 15:45:09.319284

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bb31223f935e"
down_revision: Union[str, None] = "2bac081ab9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("idx_dataset_name", "datasets", ["name"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_dataset_name", table_name="datasets")
