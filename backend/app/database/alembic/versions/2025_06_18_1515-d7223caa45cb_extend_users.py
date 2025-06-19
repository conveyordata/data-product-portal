"""extend users

Revision ID: d7223caa45cb
Revises: 137cce3079d2
Create Date: 2025-06-18 15:15:05.620663

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d7223caa45cb"
down_revision: Union[str, None] = "137cce3079d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("location", sa.String, nullable=True))
    op.add_column("users", sa.Column("phone", sa.String, nullable=True))
    op.add_column(
        "users", sa.Column("last_login", sa.DateTime(timezone=False), nullable=True)
    )
    op.add_column("users", sa.Column("bio", sa.String, nullable=True))
    op.add_column("users", sa.Column("profile_picture", sa.String, nullable=True))


def downgrade() -> None:
    op.drop_column("users", "profile_picture")
    op.drop_column("users", "bio")
    op.drop_column("users", "last_login")
    op.drop_column("users", "phone")
    op.drop_column("users", "location")
