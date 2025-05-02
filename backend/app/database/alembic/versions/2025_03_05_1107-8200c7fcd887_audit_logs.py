"""audit logs

Revision ID: 8200c7fcd887
Revises: 2a58b7ce3cea
Create Date: 2025-03-05 11:07:09.880051

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.events.enum import Type
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "8200c7fcd887"
down_revision: Union[str, None] = "2a58b7ce3cea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("status_code", sa.Integer, nullable=False),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("subject_id", sa.UUID, nullable=True),
        sa.Column("target_id", sa.UUID, nullable=True),
        sa.Column("ip", sa.String, nullable=True),
        sa.Column("user_agent", sa.String, nullable=True),
        sa.Column("response", sa.String, nullable=True),
        sa.Column("query_parameters", sa.String, nullable=True),
        sa.Column("path_parameters", sa.String, nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
        sa.PrimaryKeyConstraint("id"),
    )
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
    op.drop_table("audit_logs")
