"""technical asset access modes

Revision ID: b15295e377ac
Revises: c3d8a1f56e42
Create Date: 2026-08-03 09:15:10.090671

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "b15295e377ac"
down_revision: Union[str, None] = "c3d8a1f56e42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "access_modes",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False
        ),
        sa.Column("name", sa.Text()),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.create_table(
        "technical_asset_access_modes",
        sa.Column(
            "technical_asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_outputs.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
            index=True,
        ),
        sa.Column(
            "access_mode_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("access_modes.id"),
            nullable=False,
            primary_key=True,
            index=True,
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
    )
    op.add_column(
        "input_port_requests",
        sa.Column(
            "access_mode_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("access_modes.id"),
            nullable=True,
            primary_key=True,
            index=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("input_port_requests", "access_mode_id")
    op.drop_table("technical_asset_access_modes")
    op.drop_table("access_modes")
