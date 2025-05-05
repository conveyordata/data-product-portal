"""add prototype to roles

Revision ID: c9b48c675202
Revises: c02e4638423f
Create Date: 2025-04-01 15:26:22.491487

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.roles.schema import Prototype

# revision identifiers, used by Alembic.
revision: str = "c9b48c675202"
down_revision: Union[str, None] = "c02e4638423f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "roles",
        sa.Column(
            "prototype", sa.SmallInteger, nullable=False, default=Prototype.CUSTOM
        ),
    )


def downgrade() -> None:
    op.drop_column("roles", "prototype")
