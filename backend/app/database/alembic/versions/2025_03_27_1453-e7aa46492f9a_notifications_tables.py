"""Notifications tables

Revision ID: e7aa46492f9a
Revises: c02e4638423f
Create Date: 2025-03-27 14:53:15.943060

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.notifications.notification_types import NotificationTypes
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "e7aa46492f9a"
down_revision: Union[str, None] = "c02e4638423f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the "notifications" table
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("notification_type", sa.Enum(NotificationTypes)),
        sa.Column("notification_origin", sa.String),
        sa.Column(
            "data_product_dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("data_products_datasets.id"),
            nullable=True,
        ),
        sa.Column(
            "data_output_dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("data_outputs_datasets.id"),
            nullable=True,
        ),
        sa.Column(
            "data_product_membership_id",
            UUID(as_uuid=True),
            sa.ForeignKey("data_product_memberships.id"),
            nullable=True,
        ),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )

    # Create the "notification_interactions" table
    op.create_table(
        "notification_interactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "notification_id",
            UUID(as_uuid=True),
            sa.ForeignKey("notifications.id"),
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("last_seen", sa.DateTime, nullable=True),
        sa.Column("last_interaction", sa.DateTime, nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("notification_interactions")
    op.drop_table("notification_configurations")
