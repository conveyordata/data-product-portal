"""add foreign key on data quality output ports

Revision ID: d838b01d5e6a
Revises: a1b2c3d4e5f6
Create Date: 2026-03-20 15:14:27.775713

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d838b01d5e6a"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add foreign key constraint to output_port_data_quality_summaries table
    op.create_foreign_key(
        "fk_output_port_data_quality_summaries_output_port_id",
        "output_port_data_quality_summaries",
        "datasets",
        ["output_port_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_output_port_data_quality_summaries_output_port_id",
        "output_port_data_quality_summaries",
        type_="foreignkey",
    )
