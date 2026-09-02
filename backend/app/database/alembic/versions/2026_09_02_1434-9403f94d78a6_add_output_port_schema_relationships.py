"""add output port schema relationships

Revision ID: 9403f94d78a6
Revises: 676a29542f0b
Create Date: 2026-09-02 14:34:17.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "9403f94d78a6"
down_revision: Union[str, None] = "676a29542f0b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "output_port_schema_relationships",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "source_property_id",
            sa.UUID,
            sa.ForeignKey("output_port_schema_properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_property_id",
            sa.UUID,
            sa.ForeignKey("output_port_schema_properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.Text(),
            nullable=False,
            server_default="foreignKey",
        ),
    )


def downgrade() -> None:
    op.drop_table("output_port_schema_relationships")
