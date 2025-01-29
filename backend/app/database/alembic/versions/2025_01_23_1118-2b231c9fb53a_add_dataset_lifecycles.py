"""add dataset lifecycles

Revision ID: 2b231c9fb53a
Revises: a5c04c8cb4f1
Create Date: 2025-01-23 11:18:06.952551

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "2b231c9fb53a"
down_revision: Union[str, None] = "a5c04c8cb4f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.add_column(
        "datasets",
        sa.Column(
            "lifecycle_id",
            UUID,
            sa.ForeignKey("data_product_lifecycles.id"),
        ),
    )


def downgrade() -> None:
    op.drop_column("datasets", "lifecycle_id")
