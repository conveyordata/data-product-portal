"""empty message

Revision ID: 0ec371fe987b
Revises: 5477aa0d86f0, 85073aa08de4
Create Date: 2024-09-18 18:49:58.243125

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "0ec371fe987b"
down_revision: Union[str, tuple[str, str]] = ("5477aa0d86f0", "85073aa08de4")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
