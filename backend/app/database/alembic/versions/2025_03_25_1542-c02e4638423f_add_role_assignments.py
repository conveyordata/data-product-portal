"""Add role assignments

Revision ID: c02e4638423f
Revises: aeffee7f1029
Create Date: 2025-03-25 15:42:49.337247

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.role_assignments.enums import DecisionStatus
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "c02e4638423f"
down_revision: Union[str, None] = "aeffee7f1029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "role_assignments_data_product",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column(
            "data_product_id",
            sa.UUID,
            sa.ForeignKey("data_products.id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_id", sa.UUID, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column(
            "decision",
            sa.Enum(DecisionStatus),
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
    op.create_table(
        "role_assignments_dataset",
        sa.Column("id", sa.UUID, primary_key=True, nullable=False),
        sa.Column("dataset_id", sa.UUID, sa.ForeignKey("datasets.id"), nullable=False),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_id", sa.UUID, sa.ForeignKey("roles.id"), nullable=True),
        sa.Column(
            "decision",
            sa.Enum(DecisionStatus),
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
    op.drop_table("role_assignments_data_product")
    op.drop_table("role_assignments_dataset")
