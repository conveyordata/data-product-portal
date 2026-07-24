"""Add revoke tracking to input port requests

Revision ID: c3d8a1f56e42
Revises: b1e7c4a9d3f2
Create Date: 2026-07-22 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c3d8a1f56e42"
down_revision: Union[str, None] = "b1e7c4a9d3f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "input_port_requests",
        sa.Column("revoked_at", sa.DateTime(timezone=False), nullable=True),
    )
    op.add_column(
        "input_port_requests",
        sa.Column("revoked_by_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "input_port_requests_revoked_by_id_fkey",
        "input_port_requests",
        "users",
        ["revoked_by_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "input_port_requests_revoked_by_id_fkey",
        "input_port_requests",
        type_="foreignkey",
    )
    op.drop_column("input_port_requests", "revoked_by_id")
    op.drop_column("input_port_requests", "revoked_at")
