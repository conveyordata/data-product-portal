"""add output port schema model

Revision ID: 8aa8df18d6ff
Revises: 8b489330a188
Create Date: 2026-05-18 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "8aa8df18d6ff"
down_revision: Union[str, None] = "8b489330a188"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "output_port_schema_objects",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "output_port_id",
            sa.UUID,
            sa.ForeignKey("datasets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("logical_type", sa.Text(), nullable=True),
        sa.Column("physical_type", sa.Text(), nullable=True),
        sa.Column("physical_name", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "position",
            sa.SmallInteger(),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "output_port_schema_properties",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "schema_object_id",
            sa.UUID,
            sa.ForeignKey("output_port_schema_objects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_property_id",
            sa.UUID,
            sa.ForeignKey("output_port_schema_properties.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("business_name", sa.Text(), nullable=True),
        sa.Column("logical_type", sa.Text(), nullable=True),
        sa.Column("physical_type", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("required", sa.Boolean(), nullable=False, default=False),
        sa.Column("unique", sa.Boolean(), nullable=False, default=False),
        sa.Column("primary_key", sa.Boolean(), nullable=False, default=False),
        sa.Column("partitioned", sa.Boolean(), nullable=False, default=False),
        sa.Column("partition_key_position", sa.SmallInteger(), nullable=True),
        sa.Column("primary_key_position", sa.SmallInteger(), nullable=True),
        sa.Column("examples", sa.JSON(), nullable=True),
        sa.Column(
            "position",
            sa.SmallInteger(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_table("output_port_schema_properties")
    op.drop_table("output_port_schema_objects")
