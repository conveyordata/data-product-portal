"""event history

Revision ID: f967668dbf54
Revises: 886fc49acbda
Create Date: 2025-05-06 16:28:28.024986

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.events.enum import Type
from app.shared.model import utcnow


# revision identifiers, used by Alembic.
revision: str = 'f967668dbf54'
down_revision: Union[str, None] = '886fc49acbda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("subject_id", sa.UUID),
        sa.Column("target_id", sa.UUID, nullable=True),
        sa.Column("subject_type", sa.Enum(Type)),
        sa.Column("target_type", sa.Enum(Type), nullable=True),
        sa.Column("deleted_subject_identifier", sa.String, nullable=True),
        sa.Column("deleted_target_identifier", sa.String, nullable=True),
        sa.Column("actor_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("domain_id", sa.UUID, sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("events")
    op.execute('DROP TYPE "type"')