"""Notifications tables

Revision ID: e7aa46492f9a
Revises: 2a58b7ce3cea
Create Date: 2025-03-05 14:53:15.943060

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

from app.notifications.notification_types import NotificationTypes

# revision identifiers, used by Alembic.
revision: str = "e7aa46492f9a"
down_revision: Union[str, None] = "2a58b7ce3cea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the "notification_configurations" table
    op.create_table(
        "notification_configurations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("configuration_type", sa.Enum(NotificationTypes)),
        sa.Column(
            "data_product_membership_id",
            UUID(as_uuid=True),
            sa.ForeignKey("data_product_memberships.id"),
        ),
        sa.Column(
            "data_product_dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("data_products_datasets.id"),
        ),
        sa.Column(
            "data_output_dataset_id",
            UUID(as_uuid=True),
            sa.ForeignKey("data_outputs_datasets.id"),
        ),
    )

    # Create the "notifications" table
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("description", sa.String, nullable=True),
        sa.Column(
            "configuration_id",
            UUID(as_uuid=True),
            sa.ForeignKey("notification_configurations.id"),
        ),
    )

    # Create the "notification_interactions" table
    op.create_table(
        "notification_interactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "notification_id", UUID(as_uuid=True), sa.ForeignKey("notifications.id")
        ),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("last_seen", sa.DateTime, nullable=True),
        sa.Column("last_interaction", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("notification_interactions")
    op.drop_table("notifications")
    op.drop_table("notification_configurations")
