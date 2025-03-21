"""Add role assignments

Revision ID: 3b18d71bcaba
Revises: 269e6dbd565c
Create Date: 2025-03-21 16:31:41.325704

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.role_assignments.enums import DecisionStatus
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "3b18d71bcaba"
down_revision: Union[str, None] = "269e6dbd565c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "role_assignments_data_product",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("data_product_id", sa.UUID, sa.ForeignKey("data_products.id")),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("role_id", sa.UUID, sa.ForeignKey("roles.id")),
        sa.Column("decision", sa.Enum(DecisionStatus), default=DecisionStatus.PENDING),
        sa.Column("requested_by_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("decided_by_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("decided_on", sa.DateTime(timezone=False)),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "role_assignments_dataset",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("dataset_id", sa.UUID, sa.ForeignKey("datasets.id")),
        sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("role_id", sa.UUID, sa.ForeignKey("roles.id")),
        sa.Column("decision", sa.Enum(DecisionStatus), default=DecisionStatus.PENDING),
        sa.Column("requested_by_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("decided_by_id", sa.UUID, sa.ForeignKey("users.id")),
        sa.Column("decided_on", sa.DateTime(timezone=False)),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("role_assignments_data_product")
    op.drop_table("role_assignments_dataset")
