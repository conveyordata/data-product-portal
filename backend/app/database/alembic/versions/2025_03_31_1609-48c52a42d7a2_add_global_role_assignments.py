"""add global role assignments

Revision ID: 48c52a42d7a2
Revises: c02e4638423f
Create Date: 2025-03-31 16:09:19.313485

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.role_assignments.enums import DecisionStatus
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "48c52a42d7a2"
down_revision: Union[str, None] = "c02e4638423f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "role_assignments_global",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_id", sa.UUID, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column(
            "decision",
            postgresql.ENUM(DecisionStatus, create_type=False),
            default=DecisionStatus.PENDING,
            nullable=False,
        ),
        sa.Column("requested_by_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("decided_by_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("decided_on", sa.DateTime(timezone=False)),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False)),
    )


def downgrade() -> None:
    op.drop_table("role_assignments_global")
