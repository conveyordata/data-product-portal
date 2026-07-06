"""add access duration type to output port

Revision ID: 56e4e97d7294
Revises: 691b32ae42d8
Create Date: 2026-07-06 11:12:03.952990

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "56e4e97d7294"
down_revision: Union[str, None] = "691b32ae42d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "datasets",
        sa.Column(
            "data_product_access_duration_type",
            sa.String(),
            nullable=False,
            server_default="permanent",
        ),
    )
    op.add_column(
        "datasets",
        sa.Column(
            "exploration_access_duration_type",
            sa.String(),
            nullable=False,
            server_default="permanent",
        ),
    )


def downgrade() -> None:
    op.drop_column("datasets", "data_product_access_duration_type")
    op.drop_column("datasets", "exploration_access_duration_type")
