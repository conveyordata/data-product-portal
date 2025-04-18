"""merge 48c and fd4

Revision ID: b3a391db07dd
Revises: 48c52a42d7a2, fd4d29ed5f7c
Create Date: 2025-04-16 16:57:40.634579

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "b3a391db07dd"
down_revision: Union[str, Sequence[str], None] = ("48c52a42d7a2", "fd4d29ed5f7c")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
