"""Second merge

Revision ID: 4b87ab41d95e
Revises: deff323c76ad, 79a3d8a69dec
Create Date: 2024-10-08 16:40:09.032093

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "4b87ab41d95e"
down_revision: Union[tuple[str, str], None] = ("deff323c76ad", "79a3d8a69dec")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
