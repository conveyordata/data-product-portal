"""Merge dataset search vector and query stats heads

Revision ID: 5b9c7e8f1234
Revises: 58c7d09c5798, 249eae21bcac
Create Date: 2025-11-21 14:15:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "5b9c7e8f1234"
down_revision: Union[tuple[str, str], None] = ("58c7d09c5798", "249eae21bcac")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op merge revision."""
    pass


def downgrade() -> None:
    """No-op merge revision."""
    pass
