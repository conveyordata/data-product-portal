"""Notifications tables

Revision ID: e7aa46492f9a
Revises: f967668dbf54
Create Date: 2025-05-28 14:53:15.943060

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "e7aa46492f9a"
down_revision: Union[str, None] = "f967668dbf54"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "event_id",
            UUID(as_uuid=True),
            sa.ForeignKey("events.id", ondelete="CASCADE"),
        ),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("notifications")
