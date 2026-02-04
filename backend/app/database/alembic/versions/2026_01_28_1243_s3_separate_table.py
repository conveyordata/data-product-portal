"""Migrate S3 configurations to separate table

Revision ID: s3_separate_table
Revises: databricks_separate_table
Create Date: 2026-01-28 12:43:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.shared.model import utcnow

# revision identifiers, used by Alembic.
revision: str = "s3_separate_table"
down_revision: Union[str, None] = "databricks_separate_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new s3_technical_asset_configurations table
    op.create_table(
        "s3_technical_asset_configurations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("data_output_configurations.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("bucket", sa.String(), nullable=True),
        sa.Column("suffix", sa.String(), nullable=True),
        sa.Column("path", sa.String(), nullable=True),
        sa.Column("created_on", sa.DateTime(timezone=False), server_default=utcnow()),
        sa.Column("updated_on", sa.DateTime(timezone=False), onupdate=utcnow()),
        sa.Column("deleted_at", sa.DateTime(timezone=False), nullable=True),
    )

    # Migrate existing S3 data
    op.execute(
        """
        INSERT INTO s3_technical_asset_configurations
            (id, bucket, suffix, path, created_on, updated_on, deleted_at)
        SELECT
            id, bucket, suffix, path, created_on, updated_on, deleted_at
        FROM data_output_configurations
        WHERE configuration_type = 'S3DataOutput'
        """
    )

    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'S3TechnicalAssetConfiguration'
        WHERE configuration_type = 'S3DataOutput'
        """
    )

    # Remove S3-specific columns from base table to avoid duplicate data
    op.execute(
        """
        UPDATE data_output_configurations
        SET
            bucket = NULL,
            suffix = NULL,
            path = NULL
        WHERE configuration_type = 'S3TechnicalAssetConfiguration'
        """
    )


def downgrade() -> None:
    # Migrate all S3 data back to base table (including newly created rows)
    op.execute(
        """
        UPDATE data_output_configurations
        SET configuration_type = 'S3DataOutput'
        WHERE configuration_type = 'S3TechnicalAssetConfiguration'
        """
    )
    op.execute(
        """
        UPDATE data_output_configurations AS base
        SET
            bucket = s3.bucket,
            suffix = s3.suffix,
            path = s3.path
        FROM s3_technical_asset_configurations AS s3
        WHERE base.id = s3.id
        """
    )

    op.drop_table("s3_technical_asset_configurations")
