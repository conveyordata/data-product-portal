"""add data outputs

Revision ID: 5477aa0d86f0
Revises: 4e61079eaf16
Create Date: 2024-07-23 11:18:30.435296

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import UUID

from app.data_outputs.status import DataOutputStatus
from app.role_assignments.enums import DecisionStatus
from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "5477aa0d86f0"
down_revision: Union[str, None] = "926e7e37f11e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_outputs",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("external_id", sa.String),
        sa.Column("name", sa.String),
        sa.Column("description", sa.String),
        sa.Column("status", sa.Enum(DataOutputStatus)),
        sa.Column("platform_id", sa.UUID, sa.ForeignKey("platforms.id")),
        sa.Column("service_id", sa.UUID, sa.ForeignKey("platform_services.id")),
        sa.Column("owner_id", sa.UUID, sa.ForeignKey("data_products.id")),
        sa.Column("configuration", sa.String),
        sa.Column("configuration_id", sa.UUID),
        sa.Column("configuration_type", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "data_output_configurations",
        sa.Column("id", sa.UUID, primary_key=True),
        sa.Column("bucket", sa.String),
        sa.Column("configuration_type", sa.String),
        sa.Column("suffix", sa.String),
        sa.Column("path", sa.String),
        sa.Column("database", sa.String),
        sa.Column("database_suffix", sa.String),
        sa.Column("table", sa.String),
        sa.Column("database_path", sa.String),
        sa.Column("table_path", sa.String),
        sa.Column("bucket_identifier", sa.String),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )
    op.create_table(
        "data_outputs_datasets",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "data_output_id", UUID(as_uuid=True), sa.ForeignKey("data_outputs.id")
        ),
        sa.Column("dataset_id", UUID(as_uuid=True), sa.ForeignKey("datasets.id")),
        sa.Column(
            "status",
            sa.Enum(DecisionStatus),
            default=DecisionStatus.PENDING,
        ),
        sa.Column("requested_by_id", UUID),
        sa.Column("requested_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("approved_by_id", UUID),
        sa.Column("approved_on", sa.DateTime(timezone=False)),
        sa.Column("denied_by_id", UUID),
        sa.Column("denied_on", sa.DateTime(timezone=False)),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime),
    )


def downgrade() -> None:
    op.drop_table("data_outputs_datasets")
    op.drop_table("data_output_configurations")
    op.drop_table("data_outputs")
