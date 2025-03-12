"""empty message

Revision ID: a5c04c8cb4f1
Revises: df605bd8b0a0, 4c49c19ee972
Create Date: 2025-01-23 11:17:57.386865

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "a5c04c8cb4f1"
down_revision: Union[tuple[str, str], None] = ("df605bd8b0a0", "4c49c19ee972")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
