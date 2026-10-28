"""add access_durations

Revision ID: 691b32ae42d8
Revises: ecaa71141f4c
Create Date: 2026-07-02 16:40:25.193825

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "691b32ae42d8"
down_revision: Union[str, None] = "ecaa71141f4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "access_durations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("abstract_data_product_type", sa.String(), nullable=False),
        sa.Column("access_duration_type", sa.String(), nullable=False),
        sa.Column("days", sa.Integer(), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("created_on", sa.DateTime(), nullable=True),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "abstract_data_product_type",
            "access_duration_type",
            name="uq_access_duration_type",
        ),
    )
    op.execute(
        """
        INSERT INTO access_durations (id, abstract_data_product_type, access_duration_type, days, is_default, created_on)
        VALUES
            ('00000000-0000-0000-0001-000000000001', 'data_products', 'permanent', null, true, NOW()),
            ('00000000-0000-0000-0001-000000000002', 'explorations', 'time_bound', 30, true, NOW())
        """
    )


def downgrade() -> None:
    op.drop_table("access_durations")
