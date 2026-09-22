"""Postgres output port plugin

Revision ID: 491c8783a7bc
Revises: 638303a2cb77
Create Date: 2026-03-02 14:54:51.833214

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "491c8783a7bc"
down_revision: Union[str, None] = "638303a2cb77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op: every install already ran this in v0.7.0-0.7.3; older installs must upgrade to 0.7.3 first.
    pass


def downgrade() -> None:
    pass
