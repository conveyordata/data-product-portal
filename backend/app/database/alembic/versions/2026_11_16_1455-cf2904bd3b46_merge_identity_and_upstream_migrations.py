"""merge identity and upstream migrations

Revision ID: cf2904bd3b46
Revises: 4b6d2a8f1c35, f9c2a3a993da
Create Date: 2026-11-16 14:55:43.675614

"""

from typing import Sequence, Union

revision: str = "cf2904bd3b46"
down_revision: Union[str, Sequence[str], None] = ("4b6d2a8f1c35", "f9c2a3a993da")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
