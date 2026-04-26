"""add output_port_cost_records table

Revision ID: 1b4af17b29f7
Revises: 63243c53dd67
Create Date: 2026-04-26 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "1b4af17b29f7"
down_revision: Union[str, None] = "63243c53dd67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "output_port_cost_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("output_port_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recorded_at", sa.Date(), nullable=False),
        sa.Column("compute_cost", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("storage_cost", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column(
            "platform_overhead_cost", sa.Numeric(precision=12, scale=4), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["output_port_id"], ["datasets.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_output_port_cost_records_output_port_id"),
        "output_port_cost_records",
        ["output_port_id"],
    )
    op.create_index(
        op.f("ix_output_port_cost_records_recorded_at"),
        "output_port_cost_records",
        ["recorded_at"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_output_port_cost_records_recorded_at"),
        table_name="output_port_cost_records",
    )
    op.drop_index(
        op.f("ix_output_port_cost_records_output_port_id"),
        table_name="output_port_cost_records",
    )
    op.drop_table("output_port_cost_records")
