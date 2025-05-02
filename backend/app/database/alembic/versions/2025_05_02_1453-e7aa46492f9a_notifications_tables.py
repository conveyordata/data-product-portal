"""Notifications tables

Revision ID: e7aa46492f9a
Revises: 886fc49acbda
Create Date: 2025-05-02 14:53:15.943060

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.notifications.enums import NotificationTypes
from app.role_assignments.enums import DecisionStatus
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "e7aa46492f9a"
down_revision: Union[str, None] = "886fc49acbda"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the "notifications" table
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("notification_type", sa.Enum(NotificationTypes)),
        sa.Column("notification_origin", sa.Enum(DecisionStatus)),
        sa.Column("data_product_dataset_id", sa.UUID),
        sa.Column("data_output_dataset_id", sa.UUID),
        sa.Column("data_product_membership_id", sa.UUID),
        sa.Column(
            "user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE")
        ),
        sa.Column("deleted_dataset_identifier", sa.String, nullable=True),
        sa.Column("deleted_data_product_identifier", sa.String, nullable=True),
        sa.Column("deleted_data_output_identifier", sa.String, nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("notifications")
